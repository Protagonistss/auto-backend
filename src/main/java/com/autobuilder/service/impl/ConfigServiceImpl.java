package com.autobuilder.service.impl;

import com.autobuilder.service.ConfigService;
import com.autobuilder.service.LlmService;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.ClassPathResource;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.nio.charset.StandardCharsets;

@Service
public class ConfigServiceImpl implements ConfigService {

    private static final Logger logger = LoggerFactory.getLogger(ConfigServiceImpl.class);
    
    private final ObjectMapper objectMapper = new ObjectMapper();
    
    @Autowired(required = false)
    private LlmService llmService;

    @Override
    public OrmGenerationResult generateOrm(MultipartFile file) {
        if (file.isEmpty()) {
            throw new IllegalArgumentException("File cannot be empty");
        }

        if (llmService == null) {
            throw new IllegalStateException("AI服务不可用，请检查配置");
        }

        try {
            // 读取上传的文件内容
            String configContent = new String(file.getBytes(), StandardCharsets.UTF_8);
            logger.info("开始处理ORM生成请求，文件大小: {} 字节", configContent.length());

            // 读取ORM提示词模板
            String promptTemplate = readOrmPromptTemplate();
            
            // 构建完整的提示词
            String fullPrompt = promptTemplate + "\n\n输入配置:\n" + configContent;

            // 调用AI生成ORM
            String aiResponse = llmService.generatePlan(fullPrompt);
            
            // 解析AI响应，提取ORM XML
            String ormXml = extractOrmXml(aiResponse);
            String entityName = extractEntityName(aiResponse);
            String tableName = extractTableName(aiResponse);

            logger.info("ORM生成完成，实体: {}, 表: {}", entityName, tableName);
            
            return new OrmGenerationResult(ormXml, entityName, tableName);

        } catch (IOException e) {
            throw new RuntimeException("读取文件失败: " + e.getMessage(), e);
        } catch (Exception e) {
            logger.error("ORM生成失败", e);
            throw new RuntimeException("ORM生成失败: " + e.getMessage(), e);
        }
    }

    private String readOrmPromptTemplate() throws IOException {
        ClassPathResource resource = new ClassPathResource("prompts/orm/orm.md");
        if (!resource.exists()) {
            throw new IllegalStateException("ORM提示词模板文件不存在: prompts/orm/orm.md");
        }
        return new String(resource.getInputStream().readAllBytes(), StandardCharsets.UTF_8);
    }

    private String extractOrmXml(String aiResponse) {
        // 提取XML部分，假设AI返回的响应中包含XML标签
        int xmlStart = aiResponse.indexOf("<orm");
        if (xmlStart == -1) {
            // 如果没有找到完整的orm标签，尝试查找任何XML标签
            xmlStart = aiResponse.indexOf("<");
        }
        
        if (xmlStart == -1) {
            throw new RuntimeException("AI响应中未找到有效的XML内容");
        }
        
        int xmlEnd = aiResponse.lastIndexOf("</orm>");
        if (xmlEnd == -1) {
            xmlEnd = aiResponse.lastIndexOf(">");
        }
        
        if (xmlEnd == -1 || xmlEnd <= xmlStart) {
            throw new RuntimeException("无法提取完整的XML内容");
        }
        
        return aiResponse.substring(xmlStart, xmlEnd + 6); // +6 to include "</orm>"
    }

    private String extractEntityName(String aiResponse) {
        // 尝试从AI响应中提取实体名称
        // 这里可以基于AI响应的结构来解析，暂时返回默认值
        return "app.module.Entity";
    }

    private String extractTableName(String aiResponse) {
        // 尝试从AI响应中提取表名
        // 这里可以基于AI响应的结构来解析，暂时返回默认值
        return "entity_table";
    }
}
