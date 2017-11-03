CREATE TABLE adms (
 id SERIAL NOT NULL,
 nome TEXT,
 email TEXT UNIQUE,
 senha TEXT
);

ALTER TABLE adms ADD CONSTRAINT PK_adms PRIMARY KEY (id);


CREATE TABLE cpu (
 modelo TEXT NOT NULL,
 nucleos INT,
 frequencia REAL,
 nTotal INT,
 nDisponivel INT,
 preco REAL
);

ALTER TABLE cpu ADD CONSTRAINT PK_cpu PRIMARY KEY (modelo);


CREATE TABLE gpu (
 modelo TEXT NOT NULL,
 nucleos INT,
 frequencia REAL,
 ram INT,
 nTotal TEXT,
 nDisponivel TEXT,
 preco REAL
);

ALTER TABLE gpu ADD CONSTRAINT PK_gpu PRIMARY KEY (modelo);


CREATE TABLE hd (
 modelo TEXT NOT NULL,
 capacidade INT,
 ssd BOOLEAN,
 nTotal INT,
 nDisponivel INT,
 preco REAL
);

ALTER TABLE hd ADD CONSTRAINT PK_hd PRIMARY KEY (modelo);


CREATE TABLE planos (
 id SERIAL NOT NULL,
 preco REAL,
 tempo INT,
 publico BOOLEAN
);

ALTER TABLE planos ADD CONSTRAINT PK_planos PRIMARY KEY (id);


CREATE TABLE ram (
 modelo TEXT NOT NULL,
 capacidade INT,
 nTotal INT,
 nDisponivel INT,
 preco REAL
);

ALTER TABLE ram ADD CONSTRAINT PK_ram PRIMARY KEY (modelo);


CREATE TABLE servidor (
 id SERIAL NOT NULL,
 cpu TEXT,
 nSlotGpu INT,
 nSlotRam INT,
 nSlotHd INT,
 os TEXT
);

ALTER TABLE servidor ADD CONSTRAINT PK_servidor PRIMARY KEY (id);


CREATE TABLE servidores (
 serverID INT NOT NULL,
 planoID INT NOT NULL
);

ALTER TABLE servidores ADD CONSTRAINT PK_servidores PRIMARY KEY (serverID,planoID);


CREATE TABLE usuarios (
 id SERIAL NOT NULL,
 nome TEXT NOT NULL,
 email TEXT NOT NULL,
 cpf CHAR(11),
 cnpj CHAR(14),
 empresa TEXT,
 senha TEXT NOT NULL
);

ALTER TABLE usuarios ADD CONSTRAINT PK_usuarios PRIMARY KEY (id);


CREATE TABLE gpu_alocado (
 serverId INT NOT NULL,
 modeloGpu TEXT NOT NULL
);

ALTER TABLE gpu_alocado ADD CONSTRAINT PK_gpu_alocado PRIMARY KEY (serverId,modeloGpu);


CREATE TABLE hd_alocado (
 serverId INT NOT NULL,
 modeloHd TEXT NOT NULL
);

ALTER TABLE hd_alocado ADD CONSTRAINT PK_hd_alocado PRIMARY KEY (serverId,modeloHd);


CREATE TABLE info_uso (
 userID INT NOT NULL,
 serverID INT NOT NULL,
 cpu_usage TEXT,
 disk_usage TEXT
);

ALTER TABLE info_uso ADD CONSTRAINT PK_info_uso PRIMARY KEY (userID,serverID);


CREATE TABLE pedidos_de_recursos (
 id SERIAL NOT NULL,
 mensagem TEXT,
 resposta TEXT,
 userID INT,
 admID INT
);

ALTER TABLE pedidos_de_recursos ADD CONSTRAINT PK_pedidos_de_recursos PRIMARY KEY (id);


CREATE TABLE planos_contratados (
 planoID INT NOT NULL,
 userID INT NOT NULL,
 dataInicio TIMESTAMP WITH TIME ZONE,
 dataFim TIMESTAMP WITH TIME ZONE
);

ALTER TABLE planos_contratados ADD CONSTRAINT PK_planos_contratados PRIMARY KEY (planoID,userID);


CREATE TABLE ram_alocado (
 serverId INT NOT NULL,
 modeloRam TEXT NOT NULL
);

ALTER TABLE ram_alocado ADD CONSTRAINT PK_ram_alocado PRIMARY KEY (serverId,modeloRam);


ALTER TABLE servidor ADD CONSTRAINT FK_servidor_0 FOREIGN KEY (cpu) REFERENCES cpu (modelo);


ALTER TABLE servidores ADD CONSTRAINT FK_servidores_0 FOREIGN KEY (serverID) REFERENCES servidor (id);
ALTER TABLE servidores ADD CONSTRAINT FK_servidores_1 FOREIGN KEY (planoID) REFERENCES planos (id);


ALTER TABLE gpu_alocado ADD CONSTRAINT FK_gpu_alocado_0 FOREIGN KEY (serverId) REFERENCES servidor (id);
ALTER TABLE gpu_alocado ADD CONSTRAINT FK_gpu_alocado_1 FOREIGN KEY (modeloGpu) REFERENCES gpu (modelo);


ALTER TABLE hd_alocado ADD CONSTRAINT FK_hd_alocado_0 FOREIGN KEY (serverId) REFERENCES servidor (id);
ALTER TABLE hd_alocado ADD CONSTRAINT FK_hd_alocado_1 FOREIGN KEY (modeloHd) REFERENCES hd (modelo);


ALTER TABLE info_uso ADD CONSTRAINT FK_info_uso_0 FOREIGN KEY (userID) REFERENCES usuarios (id);
ALTER TABLE info_uso ADD CONSTRAINT FK_info_uso_1 FOREIGN KEY (serverID) REFERENCES servidor (id);


ALTER TABLE pedidos_de_recursos ADD CONSTRAINT FK_pedidos_de_recursos_0 FOREIGN KEY (userID) REFERENCES usuarios (id);
ALTER TABLE pedidos_de_recursos ADD CONSTRAINT FK_pedidos_de_recursos_1 FOREIGN KEY (admID) REFERENCES adms (id);


ALTER TABLE planos_contratados ADD CONSTRAINT FK_planos_contratados_0 FOREIGN KEY (planoID) REFERENCES planos (id);
ALTER TABLE planos_contratados ADD CONSTRAINT FK_planos_contratados_1 FOREIGN KEY (userID) REFERENCES usuarios (id);


ALTER TABLE ram_alocado ADD CONSTRAINT FK_ram_alocado_0 FOREIGN KEY (serverId) REFERENCES servidor (id);
ALTER TABLE ram_alocado ADD CONSTRAINT FK_ram_alocado_1 FOREIGN KEY (modeloRam) REFERENCES ram (modelo);


