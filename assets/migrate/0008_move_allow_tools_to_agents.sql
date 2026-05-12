ALTER TABLE agents ADD COLUMN allow_tools TEXT;
ALTER TABLE role_templates DROP COLUMN allowed_tools;
