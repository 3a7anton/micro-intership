-- =====================================================
-- QUICKHIRE DATABASE SETUP - Complete SQL with RLS
-- Run this in Supabase SQL Editor
-- =====================================================

-- =====================================================
-- 1. CREATE TABLES
-- =====================================================

-- USERS (extended profile, links to Supabase Auth)
create table users (
  id uuid references auth.users primary key,
  full_name varchar(100),
  role varchar(20) check (role in ('student','company','admin')),
  email varchar(150),
  university varchar(200),
  student_id varchar(50),
  skills text,
  company_name varchar(150),
  industry varchar(100),
  contact_no varchar(20),
  description text,
  is_approved boolean default false,
  created_at timestamp default now()
);

-- TASKS
create table tasks (
  id serial primary key,
  company_id uuid references users(id),
  title varchar(200),
  description text,
  required_skills text,
  deliverables text,
  payment_amount numeric(10,2),
  deadline date,
  status varchar(20) default 'open',
  posted_at timestamp default now()
);

-- APPLICATIONS
create table applications (
  id serial primary key,
  task_id int references tasks(id),
  student_id uuid references users(id),
  cover_note text,
  status varchar(20) default 'pending',
  applied_at timestamp default now()
);

-- SUBMISSIONS
create table submissions (
  id serial primary key,
  application_id int references applications(id),
  file_url varchar(500),
  submitted_at timestamp default now(),
  is_approved boolean default false
);

-- PAYMENTS
create table payments (
  id serial primary key,
  submission_id int references submissions(id),
  student_id uuid references users(id),
  company_id uuid references users(id),
  amount numeric(10,2),
  status varchar(20) default 'pending',
  processed_at timestamp default now()
);

-- CERTIFICATES
create table certificates (
  id serial primary key,
  student_id uuid references users(id),
  task_id int references tasks(id),
  payment_id int references payments(id),
  issued_at timestamp default now()
);

-- REVIEWS
create table reviews (
  id serial primary key,
  reviewer_id uuid references users(id),
  reviewee_id uuid references users(id),
  task_id int references tasks(id),
  rating int check (rating between 1 and 5),
  comment text,
  created_at timestamp default now()
);

-- =====================================================
-- 2. ENABLE RLS ON ALL TABLES
-- =====================================================

alter table users enable row level security;
alter table tasks enable row level security;
alter table applications enable row level security;
alter table submissions enable row level security;
alter table payments enable row level security;
alter table certificates enable row level security;
alter table reviews enable row level security;

-- =====================================================
-- 3. USERS TABLE POLICIES
-- =====================================================

-- Users can view their own profile
create policy "Users can view own profile"
  on users for select
  using (auth.uid() = id);

-- Users can view other user profiles (for display purposes)
create policy "Anyone can view user profiles"
  on users for select
  to anon, authenticated
  using (true);

-- Users can update their own profile
create policy "Users can update own profile"
  on users for update
  using (auth.uid() = id);

-- Users can insert their own profile (during registration)
create policy "Users can insert own profile"
  on users for insert
  with check (auth.uid() = id);

-- Admin can view all users
create policy "Admin can view all users"
  on users for select
  using (
    exists (
      select 1 from users where id = auth.uid() and role = 'admin'
    )
  );

-- Admin can update all users
create policy "Admin can update all users"
  on users for update
  using (
    exists (
      select 1 from users where id = auth.uid() and role = 'admin'
    )
  );

-- Admin can delete users
create policy "Admin can delete users"
  on users for delete
  using (
    exists (
      select 1 from users where id = auth.uid() and role = 'admin'
    )
  );

-- =====================================================
-- 4. TASKS TABLE POLICIES
-- =====================================================

-- Anyone can view open tasks (for students browsing)
create policy "Anyone can view open tasks"
  on tasks for select
  to anon, authenticated
  using (status = 'open');

-- Companies can view their own tasks
create policy "Companies can view own tasks"
  on tasks for select
  using (
    company_id = auth.uid() or
    exists (
      select 1 from users where id = auth.uid() and role = 'admin'
    )
  );

-- Companies can post tasks
create policy "Companies can post tasks"
  on tasks for insert
  with check (
    company_id = auth.uid() and
    exists (
      select 1 from users where id = auth.uid() and role = 'company'
    )
  );

-- Companies can update their own tasks
create policy "Companies can update own tasks"
  on tasks for update
  using (company_id = auth.uid());

-- Companies can delete their own tasks
create policy "Companies can delete own tasks"
  on tasks for delete
  using (company_id = auth.uid());

-- Admin can view all tasks
create policy "Admin can view all tasks"
  on tasks for select
  using (
    exists (
      select 1 from users where id = auth.uid() and role = 'admin'
    )
  );

-- Admin can delete any task
create policy "Admin can delete any task"
  on tasks for delete
  using (
    exists (
      select 1 from users where id = auth.uid() and role = 'admin'
    )
  );

-- =====================================================
-- 5. APPLICATIONS TABLE POLICIES
-- =====================================================

-- Students can view their own applications
create policy "Students can view own applications"
  on applications for select
  using (
    student_id = auth.uid() or
    exists (
      select 1 from tasks t
      where t.id = applications.task_id and t.company_id = auth.uid()
    ) or
    exists (
      select 1 from users where id = auth.uid() and role = 'admin'
    )
  );

-- Students can apply for tasks
create policy "Students can apply for tasks"
  on applications for insert
  with check (
    student_id = auth.uid() and
    exists (
      select 1 from users where id = auth.uid() and role = 'student'
    )
  );

-- Companies can update applications for their tasks (accept/reject)
create policy "Companies can update applications for own tasks"
  on applications for update
  using (
    exists (
      select 1 from tasks t
      where t.id = applications.task_id and t.company_id = auth.uid()
    )
  );

-- Admin can view all applications
create policy "Admin can view all applications"
  on applications for select
  using (
    exists (
      select 1 from users where id = auth.uid() and role = 'admin'
    )
  );

-- =====================================================
-- 6. SUBMISSIONS TABLE POLICIES
-- =====================================================

-- Students can view their own submissions
create policy "Students can view own submissions"
  on submissions for select
  using (
    exists (
      select 1 from applications a
      where a.id = submissions.application_id and a.student_id = auth.uid()
    ) or
    exists (
      select 1 from tasks t
      join applications a on a.task_id = t.id
      where a.id = submissions.application_id and t.company_id = auth.uid()
    ) or
    exists (
      select 1 from users where id = auth.uid() and role = 'admin'
    )
  );

-- Students can submit work for their accepted applications
create policy "Students can submit work"
  on submissions for insert
  with check (
    exists (
      select 1 from applications a
      where a.id = submissions.application_id and a.student_id = auth.uid()
    )
  );

-- Companies can update submissions (approve/reject work)
create policy "Companies can update submissions"
  on submissions for update
  using (
    exists (
      select 1 from tasks t
      join applications a on a.task_id = t.id
      where a.id = submissions.application_id and t.company_id = auth.uid()
    )
  );

-- =====================================================
-- 7. PAYMENTS TABLE POLICIES
-- =====================================================

-- Students can view their own payments
create policy "Students can view own payments"
  on payments for select
  using (
    student_id = auth.uid() or
    company_id = auth.uid() or
    exists (
      select 1 from users where id = auth.uid() and role = 'admin'
    )
  );

-- Companies can create payments
create policy "Companies can create payments"
  on payments for insert
  with check (
    company_id = auth.uid() and
    exists (
      select 1 from users where id = auth.uid() and role = 'company'
    )
  );

-- Companies can update payments (mark as completed)
create policy "Companies can update payments"
  on payments for update
  using (company_id = auth.uid());

-- Admin can view all payments
create policy "Admin can view all payments"
  on payments for select
  using (
    exists (
      select 1 from users where id = auth.uid() and role = 'admin'
    )
  );

-- =====================================================
-- 8. CERTIFICATES TABLE POLICIES
-- =====================================================

-- Students can view their own certificates
create policy "Students can view own certificates"
  on certificates for select
  using (
    student_id = auth.uid() or
    exists (
      select 1 from users where id = auth.uid() and role = 'admin'
    )
  );

-- System/Admin can create certificates
create policy "Admin can create certificates"
  on certificates for insert
  with check (
    exists (
      select 1 from users where id = auth.uid() and role = 'admin'
    )
  );

-- =====================================================
-- 9. REVIEWS TABLE POLICIES
-- =====================================================

-- Anyone can view reviews
create policy "Anyone can view reviews"
  on reviews for select
  to anon, authenticated
  using (true);

-- Users can create reviews for completed tasks
create policy "Users can create reviews"
  on reviews for insert
  with check (
    reviewer_id = auth.uid() and
    exists (
      select 1 from applications a
      where a.student_id = auth.uid() and a.status = 'completed'
    )
  );

-- Users can update their own reviews
create policy "Users can update own reviews"
  on reviews for update
  using (reviewer_id = auth.uid());

-- =====================================================
-- 10. STORAGE SETUP
-- =====================================================

-- Create the submissions bucket (run this in Storage or use Supabase dashboard)
-- Note: Buckets are created via API or dashboard, not SQL
-- Go to Storage → New bucket → Name: "submissions" → Public: true

-- Storage policies (to be applied in Storage policies section)
-- These are shown here for reference:

-- Policy 1: Allow public access to view files
-- CREATE POLICY "Public can view submissions"
-- ON storage.objects FOR SELECT
-- USING (bucket_id = 'submissions');

-- Policy 2: Allow authenticated users to upload files
-- CREATE POLICY "Authenticated can upload to submissions"
-- ON storage.objects FOR INSERT
-- WITH CHECK (
--   bucket_id = 'submissions' AND
--   auth.role() = 'authenticated'
-- );

-- Policy 3: Allow users to update/delete their own files
-- CREATE POLICY "Users can update own submissions"
-- ON storage.objects FOR UPDATE
-- USING (
--   bucket_id = 'submissions' AND
--   owner = auth.uid()
-- );

-- =====================================================
-- 11. HELPER FUNCTIONS
-- =====================================================

-- Function to get user role
create or replace function get_user_role()
returns varchar as $$
  select role from users where id = auth.uid();
$$ language sql security definer;

-- Function to check if user is admin
create or replace function is_admin()
returns boolean as $$
  select exists (
    select 1 from users where id = auth.uid() and role = 'admin'
  );
$$ language sql security definer;

-- Function to check if user is company owner of task
create or replace function is_task_owner(task_id int)
returns boolean as $$
  select exists (
    select 1 from tasks where id = task_id and company_id = auth.uid()
  );
$$ language sql security definer;
