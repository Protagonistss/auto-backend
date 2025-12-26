package com.autobuilder.service;

public interface LlmService {

    String generatePlan(String prompt);

    String getProviderName();

    boolean isAvailable();
}