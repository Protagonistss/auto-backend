package com.autobuilder.service.impl;

import com.autobuilder.config.AiProperties;
import com.autobuilder.service.LlmService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.stereotype.Service;

@Service
@ConditionalOnProperty(name = "ai.active-provider", havingValue = "zhipu")
public class ZhipuLlmServiceImpl implements LlmService {

    private static final Logger logger = LoggerFactory.getLogger(ZhipuLlmServiceImpl.class);

    @Autowired
    private AiProperties aiProperties;

    @Override
    public String generatePlan(String prompt) {
        AiProperties.ZhipuConfig config = aiProperties.getProviders().getZhipu();
        
        if (config == null || config.getApiKey() == null || config.getApiKey().trim().isEmpty()) {
            throw new IllegalStateException("智谱AI配置不完整，请检查API密钥配置");
        }

        try {
            logger.info("开始使用智谱AI生成构建规划，模型: {}", config.getModel());
            
            // TODO: 集成智谱AI SDK
            // ai.z.openapi.Client client = new ai.z.openapi.Client(config.getApiKey());
            // 这里是智谱AI SDK的集成点
            // 目前先返回模拟结果
            
            String result = String.format(
                "智谱AI (%s) ORM生成结果：\n" +
                "根据输入配置生成以下ORM XML：\n\n" +
                "<orm x:schema=\"/nop/schema/orm/orm.xdef\" xmlns:x=\"/nop/schema/xdsl.xdef\"\n" +
                "     xmlns:biz=\"biz\" xmlns:orm=\"orm\" xmlns:ext=\"ext\">\n" +
                "    <entities>\n" +
                "        <entity name=\"app.module.Entity\" \n" +
                "                tableName=\"entity\" \n" +
                "                displayName=\"实体\"\n" +
                "                biz:type=\"entity\"\n" +
                "                registerShortName=\"true\">\n" +
                "            <columns>\n" +
                "                <column name=\"id\" code=\"ID\" propId=\"1\" stdSqlType=\"VARCHAR\" \n" +
                "                        precision=\"36\" primary=\"true\" mandatory=\"true\" \n" +
                "                        displayName=\"ID\"/>\n" +
                "                <!-- 其他字段将根据输入配置生成 -->\n" +
                "            </columns>\n" +
                "        </entity>\n" +
                "    </entities>\n" +
                "</orm>\n\n" +
                "注意：这是模拟结果，智谱AI SDK集成后将根据实际输入配置生成对应的ORM实体。",
                config.getModel()
            );
            
            logger.info("智谱AI构建规划生成完成");
            return result;
            
        } catch (Exception e) {
            logger.error("智谱AI生成构建规划失败", e);
            throw new RuntimeException("智谱AI服务异常: " + e.getMessage(), e);
        }
    }

    @Override
    public String getProviderName() {
        return "Zhipu AI";
    }

    @Override
    public boolean isAvailable() {
        AiProperties.ZhipuConfig config = aiProperties.getProviders().getZhipu();
        return config != null && 
               config.getApiKey() != null && 
               !config.getApiKey().trim().isEmpty() &&
               config.getModel() != null &&
               !config.getModel().trim().isEmpty();
    }
}