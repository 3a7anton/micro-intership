

async function login(email, password) {
  const { data, error } = await supabaseClient.auth.signInWithPassword({ email, password });
  if (error) { alert(error.message); return; }
  const { data: profile } = await supabaseClient
    .from('users').select('role').eq('id', data.user.id).single();
  if (profile.role === 'student') window.location.href = 'student/dashboard.html';
  if (profile.role === 'company') window.location.href = 'company/dashboard.html';
  if (profile.role === 'admin')   window.location.href = 'admin/dashboard.html';
}

async function registerStudent(formData) {
  const { data, error } = await supabaseClient.auth.signUp({
    email: formData.email,
    password: formData.password
  });
  if (error) { alert(error.message); return; }
  await supabaseClient.from('users').insert({
    id: data.user.id,
    full_name: formData.fullName,
    role: 'student',
    email: formData.email,
    university: formData.university,
    student_id: formData.studentId,
    skills: formData.skills
  });
  alert('Registered! Please check your email to verify.');
  window.location.href = 'login.html';
}

async function registerCompany(formData) {
  const { data, error } = await supabaseClient.auth.signUp({
    email: formData.email,
    password: formData.password
  });
  if (error) { alert(error.message); return; }
  await supabaseClient.from('users').insert({
    id: data.user.id,
    company_name: formData.companyName,
    role: 'company',
    email: formData.email,
    industry: formData.industry,
    contact_no: formData.contactNo,
    description: formData.description
  });
  alert('Registered! Please check your email to verify.');
  window.location.href = 'login.html';
}

async function logout() {
  await supabaseClient.auth.signOut();
  window.location.href = '../login.html';
}

async function checkAuth() {
  const { data: { session } } = await supabaseClient.auth.getSession();
  if (!session) window.location.href = '../login.html';
  return session.user;
}
