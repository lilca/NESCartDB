CREATE TABLE nes_cart_tbl (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    system TEXT,             -- 動作システム (例: NES-PAL)
    dump_status TEXT,        -- ダンプ状態 (例: ok)
    crc TEXT NOT NULL,       -- CRC32ハッシュ
    sha1 TEXT NOT NULL,      -- SHA1ハッシュ
    board_type TEXT,         -- 基板タイプ (例: NES-TLROM)
    mapper INTEGER,          -- マッパー番号 (例: 4)
    prg_size TEXT,           -- PRG-ROMサイズ (例: 256k)
    chr_size TEXT,           -- CHR-ROMサイズ (例: 128k)
    chip_type TEXT           -- 搭載チップ (例: MMC3C)
);

-- CRCとSHA1にインデックス（キー）を設定
CREATE UNIQUE INDEX idx_nes_cart_sha1 ON nes_cart_tbl(sha1);
CREATE INDEX idx_nes_cart_crc ON nes_cart_tbl(crc);
