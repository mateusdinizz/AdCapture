-- Fase 8: tabela de favoritos.
-- Sem tabela de usuarios — ferramenta de uso pessoal/familiar,
-- lista de favoritos compartilhada. Revisitar se necessario multiusuario.

CREATE TABLE IF NOT EXISTS favoritos (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    anuncio_id  INT NOT NULL,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (anuncio_id) REFERENCES anuncios(id) ON DELETE CASCADE,
    UNIQUE KEY uq_favorito_anuncio (anuncio_id)
);

