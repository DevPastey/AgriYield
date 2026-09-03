-- Crop-specific management allowable depletion fractions (FAO-56 p).
-- Keep this data in PostgreSQL so recommendation behavior is configurable
-- without a backend code deploy.
ALTER TABLE crops
    ADD COLUMN IF NOT EXISTS depletion_fraction NUMERIC(3,2) NOT NULL DEFAULT 0.50;

UPDATE crops
SET depletion_fraction = CASE name
    WHEN 'maize' THEN 0.55
    WHEN 'tomato' THEN 0.40
    WHEN 'cassava' THEN 0.50
    ELSE 0.50
END;
