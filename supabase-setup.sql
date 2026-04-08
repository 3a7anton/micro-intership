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


create table applications (
  id serial primary key,
  task_id int references tasks(id),
  student_id uuid references users(id),
  cover_note text,
  status varchar(20) default 'pending',
  applied_at timestamp default now()
);


create table submissions (
  id serial primary key,
  application_id int references applications(id),
  file_url varchar(500),
  submitted_at timestamp default now(),
  is_approved boolean default false
);


create table payments (
  id serial primary key,
  submission_id int references submissions(id),
  student_id uuid references users(id),
  company_id uuid references users(id),
  amount numeric(10,2),
  status varchar(20) default 'pending',
  processed_at timestamp default now()
);


create table certificates (
  id serial primary key,
  student_id uuid references users(id),
  task_id int references tasks(id),
  payment_id int references payments(id),
  issued_at timestamp default now()
);


create table reviews (
  id serial primary key,
  reviewer_id uuid references users(id),
  reviewee_id uuid references users(id),
  task_id int references tasks(id),
  rating int check (rating between 1 and 5),
  comment text,
  created_at timestamp default now()
);





alter table users enable row level security;
alter table tasks enable row level security;
alter table applications enable row level security;
alter table submissions enable row level security;
alter table payments enable row level security;
alter table certificates enable row level security;
alter table reviews enable row level security;






create policy "Users can view own profile"
  on users for select
  using (auth.uid() = id);


-- The permissive policy 'Anyone can view user profiles' has been removed to prevent data leakage.
-- If public profiles are needed in the future, create a secure view over non-sensitive columns.


create policy "Users can update own profile"
  on users for update
  using (auth.uid() = id);


create policy "Users can insert own profile"
  on users for insert
  with check (auth.uid() = id);


create policy "Admin can view all users"
  on users for select
  using (
    exists (
      select 1 from users where id = auth.uid() and role = 'admin'
    )
  );


create policy "Admin can update all users"
  on users for update
  using (
    exists (
      select 1 from users where id = auth.uid() and role = 'admin'
    )
  );


create policy "Admin can delete users"
  on users for delete
  using (
    exists (
      select 1 from users where id = auth.uid() and role = 'admin'
    )
  );






create policy "Anyone can view open tasks"
  on tasks for select
  to anon, authenticated
  using (status = 'open');


create policy "Companies can view own tasks"
  on tasks for select
  using (
    company_id = auth.uid() or
    exists (
      select 1 from users where id = auth.uid() and role = 'admin'
    )
  );


create policy "Companies can post tasks"
  on tasks for insert
  with check (
    company_id = auth.uid() and
    exists (
      select 1 from users where id = auth.uid() and role = 'company'
    )
  );


create policy "Companies can update own tasks"
  on tasks for update
  using (company_id = auth.uid());


create policy "Companies can delete own tasks"
  on tasks for delete
  using (company_id = auth.uid());


create policy "Admin can view all tasks"
  on tasks for select
  using (
    exists (
      select 1 from users where id = auth.uid() and role = 'admin'
    )
  );


create policy "Admin can delete any task"
  on tasks for delete
  using (
    exists (
      select 1 from users where id = auth.uid() and role = 'admin'
    )
  );






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


create policy "Students can apply for tasks"
  on applications for insert
  with check (
    student_id = auth.uid() and
    exists (
      select 1 from users where id = auth.uid() and role = 'student'
    )
  );


create policy "Companies can update applications for own tasks"
  on applications for update
  using (
    exists (
      select 1 from tasks t
      where t.id = applications.task_id and t.company_id = auth.uid()
    )
  );


create policy "Admin can view all applications"
  on applications for select
  using (
    exists (
      select 1 from users where id = auth.uid() and role = 'admin'
    )
  );






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


create policy "Students can submit work"
  on submissions for insert
  with check (
    exists (
      select 1 from applications a
      where a.id = submissions.application_id and a.student_id = auth.uid()
    )
  );


create policy "Companies can update submissions"
  on submissions for update
  using (
    exists (
      select 1 from tasks t
      join applications a on a.task_id = t.id
      where a.id = submissions.application_id and t.company_id = auth.uid()
    )
  );






create policy "Students can view own payments"
  on payments for select
  using (
    student_id = auth.uid() or
    company_id = auth.uid() or
    exists (
      select 1 from users where id = auth.uid() and role = 'admin'
    )
  );


create policy "Companies can create payments"
  on payments for insert
  with check (
    company_id = auth.uid() and
    exists (
      select 1 from users where id = auth.uid() and role = 'company'
    )
  );


create policy "Companies can update payments"
  on payments for update
  using (company_id = auth.uid());


create policy "Admin can view all payments"
  on payments for select
  using (
    exists (
      select 1 from users where id = auth.uid() and role = 'admin'
    )
  );






create policy "Students can view own certificates"
  on certificates for select
  using (
    student_id = auth.uid() or
    exists (
      select 1 from users where id = auth.uid() and role = 'admin'
    )
  );


create policy "Admin can create certificates"
  on certificates for insert
  with check (
    exists (
      select 1 from users where id = auth.uid() and role = 'admin'
    )
  );






create policy "Anyone can view reviews"
  on reviews for select
  to anon, authenticated
  using (true);


create policy "Users can create reviews"
  on reviews for insert
  with check (
    reviewer_id = auth.uid() and
    exists (
      select 1 from applications a
      where a.student_id = auth.uid() and a.status = 'completed'
    )
  );


create policy "Users can update own reviews"
  on reviews for update
  using (reviewer_id = auth.uid());






































create or replace function get_user_role()
returns varchar as $$
  select role from users where id = auth.uid();
$$ language sql security definer;


create or replace function is_admin()
returns boolean as $$
  select exists (
    select 1 from users where id = auth.uid() and role = 'admin'
  );
$$ language sql security definer;


create or replace function is_task_owner(task_id int)
returns boolean as $$
  select exists (
    select 1 from tasks where id = task_id and company_id = auth.uid()
  );
$$ language sql security definer;
