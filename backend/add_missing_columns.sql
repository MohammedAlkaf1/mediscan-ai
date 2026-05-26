-- Add missing columns to reports table
ALTER TABLE reports 
ADD COLUMN IF NOT EXISTS save_report BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS error_message TEXT,
ADD COLUMN IF NOT EXISTS processed_at TIMESTAMP WITH TIME ZONE;

-- Verify all columns
SELECT column_name, data_type, is_nullable
FROM information_schema.columns 
WHERE table_name = 'reports' 
ORDER BY ordinal_position;
