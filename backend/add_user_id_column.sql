-- Add user_id column to reports table
ALTER TABLE reports 
ADD COLUMN user_id UUID REFERENCES users(id) ON DELETE SET NULL;

-- Add index for better performance
CREATE INDEX IF NOT EXISTS idx_reports_user_id ON reports(user_id);

-- Verify the column was added
SELECT column_name, data_type, is_nullable
FROM information_schema.columns 
WHERE table_name = 'reports' 
AND column_name = 'user_id';
