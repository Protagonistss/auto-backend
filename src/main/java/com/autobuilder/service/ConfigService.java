package com.autobuilder.service;

import org.springframework.web.multipart.MultipartFile;

public interface ConfigService {

    OrmGenerationResult generateOrm(MultipartFile file);
    
    class OrmGenerationResult {
        private String ormXml;
        private String entityName;
        private String tableName;

        public OrmGenerationResult(String ormXml, String entityName, String tableName) {
            this.ormXml = ormXml;
            this.entityName = entityName;
            this.tableName = tableName;
        }

        public String getOrmXml() {
            return ormXml;
        }

        public void setOrmXml(String ormXml) {
            this.ormXml = ormXml;
        }

        public String getEntityName() {
            return entityName;
        }

        public void setEntityName(String entityName) {
            this.entityName = entityName;
        }

        public String getTableName() {
            return tableName;
        }

        public void setTableName(String tableName) {
            this.tableName = tableName;
        }
    }
}
