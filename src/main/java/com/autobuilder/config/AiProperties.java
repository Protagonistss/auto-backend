package com.autobuilder.config;

import org.springframework.boot.context.properties.ConfigurationProperties;

@ConfigurationProperties(prefix = "ai")
public class AiProperties {

    private String activeProvider;
    private Providers providers;

    public String getActiveProvider() {
        return activeProvider;
    }

    public void setActiveProvider(String activeProvider) {
        this.activeProvider = activeProvider;
    }

    public Providers getProviders() {
        return providers;
    }

    public void setProviders(Providers providers) {
        this.providers = providers;
    }

    public static class Providers {
        private ZhipuConfig zhipu;
        private OpenAiConfig openai;

        public ZhipuConfig getZhipu() {
            return zhipu;
        }

        public void setZhipu(ZhipuConfig zhipu) {
            this.zhipu = zhipu;
        }

        public OpenAiConfig getOpenai() {
            return openai;
        }

        public void setOpenai(OpenAiConfig openai) {
            this.openai = openai;
        }
    }

    public static class ZhipuConfig {
        private String apiKey;
        private String model;
        private String baseUrl;

        public String getApiKey() {
            return apiKey;
        }

        public void setApiKey(String apiKey) {
            this.apiKey = apiKey;
        }

        public String getModel() {
            return model;
        }

        public void setModel(String model) {
            this.model = model;
        }

        public String getBaseUrl() {
            return baseUrl;
        }

        public void setBaseUrl(String baseUrl) {
            this.baseUrl = baseUrl;
        }
    }

    public static class OpenAiConfig {
        private String apiKey;
        private String model;

        public String getApiKey() {
            return apiKey;
        }

        public void setApiKey(String apiKey) {
            this.apiKey = apiKey;
        }

        public String getModel() {
            return model;
        }

        public void setModel(String model) {
            this.model = model;
        }
    }
}