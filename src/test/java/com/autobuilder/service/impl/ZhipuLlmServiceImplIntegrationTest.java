package com.autobuilder.service.impl;

import com.autobuilder.config.AiProperties;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.condition.EnabledIfEnvironmentVariable;

import org.springframework.test.util.ReflectionTestUtils;

import static org.junit.jupiter.api.Assertions.*;

public class ZhipuLlmServiceImplIntegrationTest {

    private ZhipuLlmServiceImpl zhipuService;
    private AiProperties aiProperties;

    @BeforeEach
    void setUp() {
        aiProperties = new AiProperties();
        AiProperties.Providers providers = new AiProperties.Providers();
        AiProperties.ZhipuConfig zhipuConfig = new AiProperties.ZhipuConfig();
        
        // 优先从环境变量获取API Key，如果没有则跳过实际API调用测试
        String apiKey = System.getenv("AI_ZHIPU_API_KEY");
        if (apiKey != null && !apiKey.trim().isEmpty()) {
            zhipuConfig.setApiKey(apiKey);
            zhipuConfig.setModel("glm-4.7");
            zhipuConfig.setBaseUrl("https://open.bigmodel.cn/api/paas/v4/");
        } else {
            // 如果没有环境变量，设置空的API Key用于测试异常情况
            zhipuConfig.setApiKey(null);
        }
        
        providers.setZhipu(zhipuConfig);
        aiProperties.setProviders(providers);
        aiProperties.setActiveProvider("zhipu");
        
        zhipuService = new ZhipuLlmServiceImpl();
        ReflectionTestUtils.setField(zhipuService, "aiProperties", aiProperties);
    }

    @Test
    @EnabledIfEnvironmentVariable(named = "AI_ZHIPU_API_KEY", matches = ".*\\S+.*")
    void testBasicConnection() {
        assertTrue(zhipuService.isAvailable(), "智谱AI服务应该可用");
        
        String simplePrompt = "请简单介绍一下你自己";
        String response = zhipuService.generatePlan(simplePrompt);
        
        assertNotNull(response, "响应不应该为null");
        assertFalse(response.trim().isEmpty(), "响应不应该为空");
        assertTrue(response.length() > 10, "响应应该有实质内容");
        
        System.out.println("智谱AI响应测试通过:");
        System.out.println(response);
    }

    @Test
    @EnabledIfEnvironmentVariable(named = "AI_ZHIPU_API_KEY", matches = ".*\\S+.*")
    void testOrmGeneration() {
        String ormPrompt = "请根据以下表格配置生成ORM实体：\n" +
                          "{\"body\": {\"table\": {\"columns\": [{\"title\": \"用户名\", \"dataIndex\": \"username\"}]}}}";
        
        String response = zhipuService.generatePlan(ormPrompt);
        
        assertNotNull(response, "ORM生成响应不应该为null");
        assertFalse(response.trim().isEmpty(), "ORM生成响应不应该为空");
        
        // 检查是否包含XML结构
        assertTrue(response.contains("<orm") || response.contains("实体"), 
                  "响应应该包含ORM相关内容");
        
        System.out.println("ORM生成测试通过:");
        System.out.println(response);
    }

    @Test
    void testServiceUnavailableWithoutApiKey() {
        // 创建没有API Key的配置
        AiProperties.ZhipuConfig emptyConfig = new AiProperties.ZhipuConfig();
        aiProperties.getProviders().setZhipu(emptyConfig);
        
        assertFalse(zhipuService.isAvailable(), "没有API Key时服务应该不可用");
        
        assertThrows(IllegalStateException.class, () -> {
            zhipuService.generatePlan("test prompt");
        }, "没有API Key时应该抛出异常");
    }
}