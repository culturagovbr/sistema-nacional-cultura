BEGIN;

CREATE TABLE "planotrabalho_situacoesarquivoplano" ("id" serial NOT NULL PRIMARY KEY, "descricao" varchar(75) NOT NULL);
INSERT INTO "planotrabalho_situacoesarquivoplano" (id,descricao) VALUES ('0','Em preenchimento');
INSERT INTO "planotrabalho_situacoesarquivoplano" (id,descricao) VALUES ('1','Avaliando anexo');
INSERT INTO "planotrabalho_situacoesarquivoplano" (id,descricao) VALUES ('2','Concluída');
INSERT INTO "planotrabalho_situacoesarquivoplano" (id,descricao) VALUES ('3','Arquivo aprovado com ressalvas');
INSERT INTO "planotrabalho_situacoesarquivoplano" (id,descricao) VALUES ('4','Arquivo danificado');
INSERT INTO "planotrabalho_situacoesarquivoplano" (id,descricao) VALUES ('5','Arquivo incompleto');
INSERT INTO "planotrabalho_situacoesarquivoplano" (id,descricao) VALUES ('6','Arquivo incorreto');

ALTER TABLE "planotrabalho_criacaosistema" DROP "situacao_minuta" CASCADE;
ALTER TABLE "planotrabalho_planocultura" DROP "situacao_ata" CASCADE;
ALTER TABLE "planotrabalho_planocultura"DROP "situacao_ata_votacao" CASCADE;
ALTER TABLE "planotrabalho_planocultura" DROP "situacao_minuta" CASCADE;
ALTER TABLE "planotrabalho_planocultura" DROP "situacao_relatorio_diretrizes" CASCADE;


ALTER TABLE "planotrabalho_conselhocultural" RENAME COLUMN "situacao_ata" TO "situacao_ata_id";
ALTER TABLE "planotrabalho_conselhocultural" ALTER COLUMN "situacao_ata_id" TYPE integer USING "situacao_ata_id"::INTEGER;
CREATE INDEX "planotrabalho_conselhocul_situacao_ata_id_570fb92c71ab6ff3_uniq" ON "planotrabalho_conselhocultural" ("situacao_ata_id");
ALTER TABLE "planotrabalho_conselhocultural" ADD CONSTRAINT "D3ec9619a46bbb294fde13c60208079d" FOREIGN KEY ("situacao_ata_id") REFERENCES "planotrabalho_situacoesarquivoplano" ("id") DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE "planotrabalho_criacaosistema" RENAME COLUMN "situacao_lei_sistema" TO "situacao_lei_sistema_id";
ALTER TABLE "planotrabalho_criacaosistema" ALTER COLUMN "situacao_lei_sistema_id" TYPE integer USING "situacao_lei_sistema_id"::INTEGER;
CREATE INDEX "planotrabalho_cri_situacao_lei_sistema_id_690205a65e63ee12_uniq" ON "planotrabalho_criacaosistema" ("situacao_lei_sistema_id");
ALTER TABLE "planotrabalho_criacaosistema" ADD CONSTRAINT "D868bddfd00762a264e441f73de5753f" FOREIGN KEY ("situacao_lei_sistema_id") REFERENCES "planotrabalho_situacoesarquivoplano" ("id") DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE "planotrabalho_fundocultura" RENAME COLUMN "situacao_lei_plano" TO "situacao_lei_plano_id";
ALTER TABLE "planotrabalho_fundocultura" ALTER COLUMN "situacao_lei_plano_id" TYPE integer USING "situacao_lei_plano_id"::INTEGER;
CREATE INDEX "planotrabalho_fundo_situacao_lei_plano_id_1630ce3530bd7d0c_uniq" ON "planotrabalho_fundocultura" ("situacao_lei_plano_id");
ALTER TABLE "planotrabalho_fundocultura" ADD CONSTRAINT "D84e7dea4d2f67675648c0f6838a3853" FOREIGN KEY ("situacao_lei_plano_id") REFERENCES "planotrabalho_situacoesarquivoplano" ("id") DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE "planotrabalho_orgaogestor" RENAME COLUMN "situacao_relatorio_secretaria" TO "situacao_relatorio_secretaria_id";
ALTER TABLE "planotrabalho_orgaogestor" ALTER COLUMN "situacao_relatorio_secretaria_id" TYPE integer USING "situacao_relatorio_secretaria_id"::INTEGER;
CREATE INDEX "planotra_situacao_relatorio_secretaria_id_436d30b91e9b0cc9_uniq" ON "planotrabalho_orgaogestor" ("situacao_relatorio_secretaria_id");
ALTER TABLE "planotrabalho_orgaogestor" ADD CONSTRAINT "D2db87b2df0512219b96acf0975fe77d" FOREIGN KEY ("situacao_relatorio_secretaria_id") REFERENCES "planotrabalho_situacoesarquivoplano" ("id") DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE "planotrabalho_planocultura" RENAME COLUMN "situacao_lei_plano" TO "situacao_lei_plano_id";
ALTER TABLE "planotrabalho_planocultura" ALTER COLUMN "situacao_lei_plano_id" TYPE integer USING "situacao_lei_plano_id"::INTEGER;
CREATE INDEX "planotrabalho_plano_situacao_lei_plano_id_4270ed5b01e7c788_uniq" ON "planotrabalho_planocultura" ("situacao_lei_plano_id");
ALTER TABLE "planotrabalho_planocultura" ADD CONSTRAINT "fc36ba1eeba893fc75be1f6158a8137e" FOREIGN KEY ("situacao_lei_plano_id") REFERENCES "planotrabalho_situacoesarquivoplano" ("id") DEFERRABLE INITIALLY DEFERRED;

COMMIT;
