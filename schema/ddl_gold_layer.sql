CREATE SCHEMA IF NOT EXISTS yhct_gold;
SET search_path TO yhct_gold;

CREATE TABLE document (
    document_id     VARCHAR(20)   PRIMARY KEY,
    title           TEXT          NOT NULL,
    source_id       VARCHAR(20)   NOT NULL,   -- FK logic tới Source Registry
    author_org      VARCHAR(255)  NOT NULL,
    publish_year    INTEGER,
    doc_type        VARCHAR(50)   NOT NULL
                      CHECK (doc_type IN ('giáo trình','dược điển','hướng dẫn điều trị','bài báo khoa học')),
    license         VARCHAR(100)  NOT NULL,
    version         VARCHAR(20)   NOT NULL DEFAULT 'v1.0',
    created_at      TIMESTAMP     NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP     NOT NULL DEFAULT NOW()
);
COMMENT ON TABLE document IS 'Tài liệu nguồn dùng để trích xuất bài thuốc, dược liệu, bệnh chứng';

CREATE TABLE disease_syndrome (
    disease_id      VARCHAR(20)   PRIMARY KEY,
    name_vi         VARCHAR(255)  NOT NULL,
    category        VARCHAR(100)  NOT NULL,
    description     TEXT,
	disease_prevention_methods TEXT,
	created_at      TIMESTAMP     NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP     NOT NULL DEFAULT NOW()
);
COMMENT ON TABLE disease_syndrome IS 'Danh mục bệnh/chứng trạng theo YHCT';


CREATE TABLE symptom (
    symptom_id      VARCHAR(20)   PRIMARY KEY,
    name            VARCHAR(255)  NOT NULL,
    description     TEXT,
    created_at      TIMESTAMP     NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP     NOT NULL DEFAULT NOW()
);
COMMENT ON TABLE symptom IS 'Danh mục triệu chứng, dùng chung cho nhiều bệnh';

CREATE TABLE herbal_formula (
    formula_id           VARCHAR(20)  PRIMARY KEY,
    name_vi              VARCHAR(255) NOT NULL,
    origin_document_id    VARCHAR(20) NOT NULL,
    preparation_method    TEXT,
    usage_note            TEXT,
    created_at             TIMESTAMP   NOT NULL DEFAULT NOW(),
    updated_at             TIMESTAMP   NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_formula_document
        FOREIGN KEY (origin_document_id)
        REFERENCES document (document_id)
        ON DELETE RESTRICT   -- không cho xóa tài liệu nếu còn bài thuốc trích dẫn
);
COMMENT ON TABLE herbal_formula IS 'Bài thuốc YHCT, không lưu liều lượng cụ thể (nguyên tắc an toàn)';
CREATE INDEX idx_formula_document ON herbal_formula (origin_document_id);

CREATE TABLE herb (
    herb_id         VARCHAR(20)   PRIMARY KEY,
    name_vi         VARCHAR(255)  NOT NULL,
    origin          VARCHAR(100),
    properties      VARCHAR(255),
    created_at      TIMESTAMP     NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP     NOT NULL DEFAULT NOW()
);
COMMENT ON TABLE herb IS 'Danh mục vị thuốc/dược liệu dùng chung toàn hệ thống';

CREATE TABLE contraindication (
    contraindication_id  VARCHAR(20)  PRIMARY KEY,
    target_type           VARCHAR(20) NOT NULL
                            CHECK (target_type IN ('formula','herb')),
    target_id              VARCHAR(20) NOT NULL,
    description             TEXT       NOT NULL,
    severity                VARCHAR(20)
                            CHECK (severity IN ('nhẹ','trung bình','nghiêm trọng')),
    created_at               TIMESTAMP  NOT NULL DEFAULT NOW(),
    updated_at               TIMESTAMP  NOT NULL DEFAULT NOW()
);
COMMENT ON TABLE contraindication IS 'Chống chỉ định áp dụng cho bài thuốc hoặc vị thuốc (polymorphic reference qua target_type/target_id)';
CREATE INDEX idx_contraindication_target ON contraindication (target_type, target_id);

CREATE TABLE formula_herb (
    formula_id       VARCHAR(20) NOT NULL,
    herb_id          VARCHAR(20) NOT NULL,
    role_in_formula  VARCHAR(50),
    note             TEXT,

    dosage_amount    NUMERIC(6,2),
    dosage_unit      VARCHAR(20),
    dosage_note      TEXT,

    PRIMARY KEY (formula_id, herb_id),

    CONSTRAINT fk_fh_formula
        FOREIGN KEY (formula_id)
        REFERENCES yhct_gold.herbal_formula(formula_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_fh_herb
        FOREIGN KEY (herb_id)
        REFERENCES yhct_gold.herb(herb_id)
        ON DELETE RESTRICT
);
COMMENT ON TABLE formula_herb IS 'Quan hệ N-N: thành phần vị thuốc trong từng bài thuốc';
CREATE INDEX idx_fh_herb ON formula_herb (herb_id);
COMMENT ON COLUMN yhct_gold.formula_herb.dosage_amount IS
    'Số lượng liều dùng ghi trong tài liệu nguồn, ví dụ 9, 12, 6';

COMMENT ON COLUMN yhct_gold.formula_herb.dosage_unit IS
    'Đơn vị liều dùng, ví dụ g, ml, viên';

COMMENT ON COLUMN yhct_gold.formula_herb.dosage_note IS
    'Ghi chú bổ sung về liều dùng theo tài liệu nguồn';


CREATE TABLE formula_disease (
    formula_id           VARCHAR(20) NOT NULL,
    disease_id           VARCHAR(20) NOT NULL,
    effectiveness_note   TEXT,
    PRIMARY KEY (formula_id, disease_id),
    CONSTRAINT fk_fd_formula
        FOREIGN KEY (formula_id) REFERENCES herbal_formula (formula_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_fd_disease
        FOREIGN KEY (disease_id) REFERENCES disease_syndrome (disease_id)
        ON DELETE RESTRICT
);
COMMENT ON TABLE formula_disease IS 'Quan hệ N-N: bài thuốc điều trị bệnh/chứng nào';
CREATE INDEX idx_fd_disease ON formula_disease (disease_id);

CREATE TABLE disease_symptom (
    disease_id     VARCHAR(20) NOT NULL,
    symptom_id     VARCHAR(20) NOT NULL,
    is_primary     BOOLEAN     NOT NULL DEFAULT TRUE,
    PRIMARY KEY (disease_id, symptom_id),
    CONSTRAINT fk_ds_disease
        FOREIGN KEY (disease_id) REFERENCES disease_syndrome (disease_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_ds_symptom
        FOREIGN KEY (symptom_id) REFERENCES symptom (symptom_id)
        ON DELETE RESTRICT
);
COMMENT ON TABLE disease_symptom IS 'Quan hệ N-N: triệu chứng thuộc bệnh/chứng nào';
CREATE INDEX idx_ds_symptom ON disease_symptom (symptom_id);

-- xem thong tin cac bang vua tao
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'yhct_gold'
  AND table_type = 'BASE TABLE'
ORDER BY table_name;