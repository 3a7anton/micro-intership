

async function loadCompanyDashboard() {
  const user = await checkAuth();
  
  
  const { data: profile, error } = await supabaseClient
    .from('users')
    .select('*')
    .eq('id', user.id)
    .single();
  
  if (profile) {
    document.getElementById('welcome-msg').textContent = `Welcome, ${profile.company_name}`;
  }
  
  
  const { data: tasks } = await supabaseClient
    .from('tasks')
    .select('id, status')
    .eq('company_id', user.id);
  
  const tasksPosted = tasks ? tasks.length : 0;
  const inProgress = tasks ? tasks.filter(t => t.status === 'in_progress').length : 0;
  const completed = tasks ? tasks.filter(t => t.status === 'completed').length : 0;
  
  
  const { data: applications } = await supabaseClient
    .from('applications')
    .select('id', { count: 'exact' })
    .in('task_id', tasks?.map(t => t.id) || [0]);
  
  document.getElementById('tasks-posted').textContent = tasksPosted;
  document.getElementById('total-applications').textContent = applications?.length || 0;
  document.getElementById('in-progress').textContent = inProgress;
  document.getElementById('completed').textContent = completed;
  
  
  const { data: recentTasks } = await supabaseClient
    .from('tasks')
    .select('*')
    .eq('company_id', user.id)
    .order('posted_at', { ascending: false })
    .limit(5);
  
  const tbody = document.getElementById('recent-tasks');
  if (recentTasks && recentTasks.length > 0) {
    tbody.innerHTML = recentTasks.map(task => `
      <tr>
        <td>${task.title}</td>
        <td>${task.payment_amount} BDT</td>
        <td>${task.deadline}</td>
        <td><span class="status-${task.status}">${task.status}</span></td>
      </tr>
    `).join('');
  } else {
    tbody.innerHTML = '<tr><td colspan="4">No tasks posted yet</td></tr>';
  }
}

async function postTask(formData) {
  const user = await checkAuth();
  
  const { error } = await supabaseClient.from('tasks').insert({
    company_id: user.id,
    title: formData.title,
    description: formData.description,
    required_skills: formData.skills,
    deliverables: formData.deliverables,
    payment_amount: formData.payment,
    deadline: formData.deadline,
    status: 'open'
  });
  
  if (error) {
    alert(error.message);
  } else {
    alert('Task posted successfully!');
    window.location.href = 'my-tasks.html';
  }
}

async function loadMyTasks() {
  const user = await checkAuth();
  
  const { data: tasks, error } = await supabaseClient
    .from('tasks')
    .select('*, applications(count)')
    .eq('company_id', user.id)
    .order('posted_at', { ascending: false });
  
  const tbody = document.getElementById('tasks-list');
  if (error || !tasks || tasks.length === 0) {
    tbody.innerHTML = '<tr><td colspan="6">No tasks posted yet</td></tr>';
    return;
  }
  
  tbody.innerHTML = tasks.map(task => `
    <tr>
      <td>${task.title}</td>
      <td>${task.payment_amount} BDT</td>
      <td>${task.deadline}</td>
      <td>${task.applications?.count || 0}</td>
      <td><span class="status-${task.status}">${task.status}</span></td>
      <td><a href="review-applications.html?task_id=${task.id}" class="btn">View Applications</a></td>
    </tr>
  `).join('');
}

let currentReviewTaskId = null;

async function loadReviewApplications() {
  const user = await checkAuth();
  
  const urlParams = new URLSearchParams(window.location.search);
  currentReviewTaskId = urlParams.get('task_id');
  
  if (!currentReviewTaskId) {
    
    const { data: tasks } = await supabaseClient
      .from('tasks')
      .select('id, title')
      .eq('company_id', user.id)
      .eq('status', 'open');
    
    if (tasks && tasks.length > 0) {
      currentReviewTaskId = tasks[0].id;
      document.getElementById('task-title').textContent = tasks[0].title;
      loadApplicationsForTask(currentReviewTaskId);
    } else {
      document.getElementById('applications-list').innerHTML = '<tr><td colspan="5">No open tasks with applications</td></tr>';
    }
    return;
  }
  
  const { data: task } = await supabaseClient
    .from('tasks')
    .select('title')
    .eq('id', currentReviewTaskId)
    .eq('company_id', user.id)
    .single();
  
  if (task) {
    document.getElementById('task-title').textContent = task.title;
  }
  
  loadApplicationsForTask(currentReviewTaskId);
}

async function loadApplicationsForTask(taskId) {
  const { data: applications, error } = await supabaseClient
    .from('applications')
    .select('*, student:users(full_name, university, skills), applied_at, id, status')
    .eq('task_id', taskId)
    .order('applied_at', { ascending: false });
  
  const tbody = document.getElementById('applications-list');
  if (error || !applications || applications.length === 0) {
    tbody.innerHTML = '<tr><td colspan="5">No applications yet</td></tr>';
    return;
  }
  
  tbody.innerHTML = applications.map(app => {
    let actions = '';
    if (app.status === 'pending') {
      actions = `
        <a href="#" class="btn" onclick="acceptApplication(${app.id}, ${taskId}); return false;">Accept</a>
        <a href="#" class="btn-grey" onclick="rejectApplication(${app.id}); return false;">Reject</a>
      `;
    } else {
      actions = `<span class="status-${app.status}">${app.status}</span>`;
    }
    return `
      <tr>
        <td>${app.student?.full_name || 'N/A'}</td>
        <td>${app.student?.university || 'N/A'}</td>
        <td>${app.student?.skills || 'N/A'}</td>
        <td>${new Date(app.applied_at).toLocaleDateString()}</td>
        <td>${actions}</td>
      </tr>
    `;
  }).join('');
}

async function acceptApplication(appId, taskId) {
  await supabaseClient.from('applications')
    .update({ status: 'accepted' })
    .eq('id', appId);
  
  await supabaseClient.from('tasks')
    .update({ status: 'in_progress' })
    .eq('id', taskId);
  
  alert('Application accepted!');
  loadApplicationsForTask(taskId);
}

async function rejectApplication(appId) {
  await supabaseClient.from('applications')
      .update({ status: 'rejected' })
      .eq('id', appId);
  
  alert('Application rejected');
  location.reload();
}

async function loadCompanyProfile() {
  const user = await checkAuth();
  
  const { data: profile, error } = await supabaseClient
    .from('users')
    .select('*')
    .eq('id', user.id)
    .single();
  
  if (profile) {
    document.getElementById('profile-company-name').textContent = profile.company_name;
    document.getElementById('profile-industry').textContent = profile.industry;
    document.getElementById('profile-email').textContent = profile.email;
    document.getElementById('profile-contact').textContent = profile.contact_no;
    document.getElementById('profile-description').textContent = profile.description;
    
    
    document.getElementById('edit-company-name').value = profile.company_name;
    document.getElementById('edit-industry').value = profile.industry;
    document.getElementById('edit-contact').value = profile.contact_no;
    document.getElementById('edit-description').value = profile.description;
  }
}

async function updateCompanyProfile(formData) {
  const user = await checkAuth();
  
  const { error } = await supabaseClient
      .from('users')
      .update({
      company_name: formData.companyName,
      industry: formData.industry,
      contact_no: formData.contactNo,
      description: formData.description
    })
    .eq('id', user.id);
  
  if (error) {
    alert(error.message);
  } else {
    alert('Profile updated successfully!');
    loadCompanyProfile();
  }
}
