-- 1. COLLEGES TABLE (Parent)
CREATE TABLE IF NOT EXISTS colleges (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    name text NOT NULL,
    state text NOT NULL,
    pincode text,
    college_type text, -- Govt, Private, Deemed
    management_type text,
    CONSTRAINT unique_college_identity UNIQUE (name, state)
);

-- 2. DEPARTMENTS TABLE (Child)
CREATE TABLE IF NOT EXISTS departments (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    college_id uuid REFERENCES colleges(id) ON DELETE CASCADE,
    degree text NOT NULL, -- MD, MS, DNB, Diploma
    course_name text NOT NULL, -- e.g., Radio Diagnosis, Pediatrics
    CONSTRAINT unique_course_per_college UNIQUE (college_id, degree, course_name)
);

-- 3. ADVANCED REVIEWS TABLE (Interaction)
CREATE TABLE IF NOT EXISTS reviews (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    college_id uuid REFERENCES colleges(id) ON DELETE CASCADE,
    dept_id uuid REFERENCES departments(id) ON DELETE CASCADE,
    
    -- Numerical Parameters (1-5 Sliders)
    academics_rating integer CHECK (academics_rating BETWEEN 1 AND 5),
    clinical_exposure_rating integer CHECK (clinical_exposure_rating BETWEEN 1 AND 5),
    infrastructure_rating integer CHECK (infrastructure_rating BETWEEN 1 AND 5),
    hands_on_rating integer CHECK (hands_on_rating BETWEEN 1 AND 5),
    stipend_rating integer CHECK (stipend_rating BETWEEN 1 AND 5),
    toxicity_rating integer CHECK (toxicity_rating BETWEEN 1 AND 5), -- 5 is Highly Toxic
    
    -- Metadata & Tags
    resident_year text, -- JR1, JR2, JR3, SR
    tags text[], -- Array of hashtags like {'#highly_toxic', '#good_exposure'}
    
    -- Text Feedback Logic
    raw_comment text, -- Hidden from public (Internal use)
    ai_sanitized_comment text, -- Publicly visible (AI Washed)
    
    created_at timestamp with time zone DEFAULT now()
);

-- 4. ANALYTICS VIEW (The "Brain" for the App)
CREATE OR REPLACE VIEW department_analytics AS
SELECT 
    dept_id,
    COUNT(id) as total_reviews,
    ROUND(AVG(academics_rating), 1) as avg_academics,
    ROUND(AVG(clinical_exposure_rating), 1) as avg_clinical,
    ROUND(AVG(6 - toxicity_rating), 1) as culture_score, -- Inverting: 5 toxicity becomes 1 score
    
    -- Overall Weighted Score
    ROUND(AVG((academics_rating + clinical_exposure_rating + infrastructure_rating + hands_on_rating + stipend_rating + (6 - toxicity_rating)) / 6.0), 1) as overall_rating,
    
    -- Unique Tag Aggregator for the Tag Cloud
    (SELECT array_agg(DISTINCT t) FROM (SELECT unnest(tags) FROM reviews r2 WHERE r2.dept_id = reviews.dept_id) AS dt(t)) as department_tags
FROM 
    reviews
GROUP BY 
    dept_id;

