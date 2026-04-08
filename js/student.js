

async function loadStudentDashboard() {
  const user = await checkAuth();
  
  
  const { data: profile, error } = await supabaseClient
    .from('users')
    .select('*')
    .eq('id', user.id)
    .single();
  
  if (profile) {
    document.getElementById('welcome-msg').textContent = `Welcome, ${profile.full_name}`;
  }
  
  
  const { data: applications } = await supabaseClient
    .from('applications')
    .select('status')
    .eq('student_id', user.id);
  
  let sent = 0, inProgress = 0, completed = 0;
  if (applications) {
    sent = applications.length;
    inProgress = applications.filter(a => a.status === 'accepted').length;
    completed = applications.filter(a => a.status === 'completed').length;
  }
  
  document.getElementById('applications-sent').textContent = sent;
  document.getElementById('in-progress').textContent = inProgress;
  document.getElementById('completed').textContent = completed;
  
  
  const { data: payments } = await supabaseClient
    .from('payments')
    .select('amount')
    .eq('student_id', user.id)
    .eq('status', 'completed');
  
  const totalEarned = payments ? payments.reduce((sum, p) => sum + p.amount, 0) : 0;
  document.getElementById('total-earned').textContent = totalEarned + ' BDT';
  
  
  const { data: recentApps } = await supabaseClient
    .from('applications')
    .select('*, tasks(title, company:users(full_name)), applied_at, status')
    .eq('student_id', user.id)
    .order('applied_at', { ascending: false })
    .limit(5);
  
  const tbody = document.getElementById('recent-applications');
  if (recentApps && recentApps.length > 0) {
    tbody.innerHTML = recentApps.map(app => `
      <tr>
        <td>${app.tasks?.title || 'N/A'}</td>
        <td>${app.company?.full_name || 'N/A'}</td>
        <td><span class="status-${app.status}">${app.status}</span></td>
        <td>${new Date(app.applied_at).toLocaleDateString()}</td>
      </tr>
    `).join('');
  } else {
    tbody.innerHTML = '<tr><td colspan="4">No applications yet</td></tr>';
  }
}

let allTasks = [];

async function loadBrowseTasks() {
  await checkAuth();
  
  const { data: tasks, error } = await supabaseClient
    .from('tasks')
    .select('*, company:users(full_name)')
    .eq('status', 'open')
    .order('posted_at', { ascending: false });
  
  if (error) { console.log(error); return; }
  
  allTasks = tasks || [];
  renderTasks(allTasks);
}

function renderTasks(tasks) {
  const container = document.getElementById('task-list');
  container.innerHTML = '';
  
  if (tasks.length === 0) {
    container.innerHTML = '<p>No tasks available</p>';
    return;
  }
  
  tasks.forEach(task => {
    const div = document.createElement('div');
    div.className = 'card';
    div.innerHTML = `
      <h3>${task.title}</h3>
      <p><b>Company:</b> ${task.company?.full_name || 'N/A'}</p>
      <p><b>Skills:</b> ${task.required_skills}</p>
      <p><b>Payment:</b> ${task.payment_amount} BDT</p>
      <p><b>Deadline:</b> ${task.deadline}</p>
      <a href="task-detail.html?id=${task.id}" class="btn">View & Apply</a>
    `;
    container.appendChild(div);
  });
}

function filterTasks(query) {
  const filtered = allTasks.filter(task => 
    task.title.toLowerCase().includes(query.toLowerCase()) ||
    task.required_skills.toLowerCase().includes(query.toLowerCase())
  );
  renderTasks(filtered);
}

let currentTaskId = null;

async function loadTaskDetail() {
  const user = await checkAuth();
  
  const urlParams = new URLSearchParams(window.location.search);
  currentTaskId = urlParams.get('id');
  
  if (!currentTaskId) {
    alert('No task specified');
    window.location.href = 'browse.html';
    return;
  }
  
  const { data: task, error } = await supabaseClient
    .from('tasks')
    .select('*, company:users(full_name)')
    .eq('id', currentTaskId)
    .single();
  
  if (error || !task) {
    alert('Task not found');
    window.location.href = 'browse.html';
    return;
  }
  
  document.getElementById('task-title').textContent = task.title;
  document.getElementById('task-description').textContent = task.description;
  document.getElementById('task-skills').textContent = task.required_skills;
  document.getElementById('task-deliverables').textContent = task.deliverables;
  document.getElementById('task-payment').textContent = task.payment_amount;
  document.getElementById('task-deadline').textContent = task.deadline;
  document.getElementById('company-name').textContent = task.company?.full_name || 'N/A';
}

async function submitApplication(coverNote) {
  const user = await checkAuth();
  
  if (!currentTaskId) return;
  
  const { error } = await supabaseClient.from('applications').insert({
    task_id: currentTaskId,
    student_id: user.id,
    cover_note: coverNote,
    status: 'pending'
  });
  
  if (error) {
    alert(error.message);
  } else {
    alert('Application submitted successfully!');
    window.location.href = 'applications.html';
  }
}

async function loadApplications() {
  const user = await checkAuth();
  
  const { data: applications, error } = await supabaseClient
    .from('applications')
    .select('*, tasks(title, company:users(full_name)), applied_at, status, id')
    .eq('student_id', user.id)
    .order('applied_at', { ascending: false });
  
  const tbody = document.getElementById('applications-list');
  if (error || !applications || applications.length === 0) {
    tbody.innerHTML = '<tr><td colspan="5">No applications yet</td></tr>';
    return;
  }
  
  tbody.innerHTML = applications.map(app => {
    let action = '-';
    if (app.status === 'accepted') {
      action = `<a href="submit-work.html?app_id=${app.id}" class="btn">Upload Work</a>`;
    }
    return `
      <tr>
        <td>${app.tasks?.title || 'N/A'}</td>
        <td>${app.tasks?.company?.full_name || 'N/A'}</td>
        <td>${new Date(app.applied_at).toLocaleDateString()}</td>
        <td><span class="status-${app.status}">${app.status}</span></td>
        <td>${action}</td>
      </tr>
    `;
  }).join('');
}

async function loadSubmitWorkPage() {
  const user = await checkAuth();
  
  const urlParams = new URLSearchParams(window.location.search);
  const appId = urlParams.get('app_id');
  
  if (!appId) {
    alert('No application specified');
    window.location.href = 'applications.html';
    return;
  }
  
  
  window.currentApplicationId = appId;
  
  const { data: app, error } = await supabaseClient
    .from('applications')
    .select('*, tasks(title, deadline)')
    .eq('id', appId)
    .eq('student_id', user.id)
    .single();
  
  if (error || !app) {
    alert('Application not found');
    window.location.href = 'applications.html';
    return;
  }
  
  document.getElementById('task-name').textContent = app.tasks?.title || 'N/A';
  document.getElementById('task-deadline').textContent = app.tasks?.deadline || 'N/A';
}

async function submitWork(file) {
  const user = await checkAuth();
  
  if (!window.currentApplicationId) {
    alert('No application specified');
    return;
  }
  
  
  const fileName = `${user.id}_${Date.now()}_${file.name}`;
  const { data: uploadData, error: uploadError } = await supabaseClient.storage
    .from('submissions')
    .upload(fileName, file);
  
  if (uploadError) {
    alert('Upload failed: ' + uploadError.message);
    return;
  }
  
  
  const { data: { publicUrl } } = supabaseClient.storage
    .from('submissions')
    .getPublicUrl(fileName);
  
  
  const { error } = await supabaseClient.from('submissions').insert({
    application_id: window.currentApplicationId,
    file_url: publicUrl
  });
  
  if (error) {
    alert(error.message);
  } else {
    alert('Work submitted successfully!');
    window.location.href = 'applications.html';
  }
}

async function loadCertificates() {
  const user = await checkAuth();
  
  const { data: certificates, error } = await supabaseClient
    .from('certificates')
    .select('*, tasks(title, company:users(full_name)), issued_at')
    .eq('student_id', user.id)
    .order('issued_at', { ascending: false });
  
  const container = document.getElementById('certificates-list');
  if (error || !certificates || certificates.length === 0) {
    container.innerHTML = '<p>No certificates yet</p>';
    return;
  }
  
  container.innerHTML = certificates.map(cert => `
    <div class="card">
      <h3>${cert.tasks?.title || 'N/A'}</h3>
      <p><b>Company:</b> ${cert.tasks?.company?.full_name || 'N/A'}</p>
      <p><b>Issued:</b> ${new Date(cert.issued_at).toLocaleDateString()}</p>
      <a href="#" class="btn" onclick="alert('Certificate download feature coming soon'); return false;">Download</a>
    </div>
  `).join('');
}

async function loadEarnings() {
  const user = await checkAuth();
  
  const { data: payments, error } = await supabaseClient
    .from('payments')
    .select('*, tasks(title, company:users(full_name)), amount, processed_at, status')
    .eq('student_id', user.id)
    .order('processed_at', { ascending: false });
  
  const tbody = document.getElementById('earnings-list');
  const totalEarnings = payments ? payments.reduce((sum, p) => sum + (p.status === 'completed' ? p.amount : 0), 0) : 0;
  document.getElementById('total-earnings').textContent = totalEarnings + ' BDT';
  
  if (error || !payments || payments.length === 0) {
    tbody.innerHTML = '<tr><td colspan="5">No earnings yet</td></tr>';
    return;
  }
  
  tbody.innerHTML = payments.map(payment => `
    <tr>
      <td>${payment.tasks?.title || 'N/A'}</td>
      <td>${payment.tasks?.company?.full_name || 'N/A'}</td>
      <td>${payment.amount} BDT</td>
      <td>${new Date(payment.processed_at).toLocaleDateString()}</td>
      <td><span class="status-${payment.status}">${payment.status}</span></td>
    </tr>
  `).join('');
}

async function loadStudentProfile() {
  const user = await checkAuth();
  
  const { data: profile, error } = await supabaseClient
    .from('users')
    .select('*')
    .eq('id', user.id)
    .single();
  
  if (profile) {
    document.getElementById('profile-name').textContent = profile.full_name;
    document.getElementById('profile-university').textContent = profile.university;
    document.getElementById('profile-student-id').textContent = profile.student_id;
    document.getElementById('profile-email').textContent = profile.email;
    document.getElementById('profile-skills').textContent = profile.skills;
    
    
    document.getElementById('edit-name').value = profile.full_name;
    document.getElementById('edit-university').value = profile.university;
    document.getElementById('edit-skills').value = profile.skills;
  }
}

async function updateProfile(formData) {
  const user = await checkAuth();
  
  const { error } = await supabaseClient
    .from('users')
    .update({
      full_name: formData.fullName,
      university: formData.university,
      skills: formData.skills
    })
    .eq('id', user.id);
  
  if (error) {
    alert(error.message);
  } else {
    alert('Profile updated successfully!');
    loadStudentProfile();
  }
}
