// Admin page logic

async function loadAdminDashboard() {
  await checkAuth();
  
  // Fetch total users by role
  const { data: users } = await supabaseClient
    .from('users')
    .select('role');
  
  const totalUsers = users ? users.length : 0;
  const totalStudents = users ? users.filter(u => u.role === 'student').length : 0;
  const totalCompanies = users ? users.filter(u => u.role === 'company').length : 0;
  
  // Fetch total tasks
  const { data: tasksCount } = await supabaseClient
    .from('tasks')
    .select('id', { count: 'exact' });
  
  // Fetch total certificates
  const { data: certCount } = await supabaseClient
    .from('certificates')
    .select('id', { count: 'exact' });
  
  document.getElementById('total-users').textContent = totalUsers;
  document.getElementById('total-students').textContent = totalStudents;
  document.getElementById('total-companies').textContent = totalCompanies;
  document.getElementById('total-tasks').textContent = tasksCount?.length || 0;
  document.getElementById('total-certificates').textContent = certCount?.length || 0;
  
  // Recent activity - show latest tasks
  const { data: recentTasks } = await supabaseClient
    .from('tasks')
    .select('title, posted_at')
    .order('posted_at', { ascending: false })
    .limit(5);
  
  const tbody = document.getElementById('recent-activity');
  if (recentTasks && recentTasks.length > 0) {
    tbody.innerHTML = recentTasks.map(task => `
      <tr>
        <td>Task Posted</td>
        <td>${task.title}</td>
        <td>${new Date(task.posted_at).toLocaleDateString()}</td>
      </tr>
    `).join('');
  } else {
    tbody.innerHTML = '<tr><td colspan="3">No recent activity</td></tr>';
  }
}

async function loadUsers() {
  await checkAuth();
  
  const { data: users, error } = await supabaseClient
    .from('users')
    .select('*')
    .order('created_at', { ascending: false });
  
  const tbody = document.getElementById('users-list');
  if (error || !users || users.length === 0) {
    tbody.innerHTML = '<tr><td colspan="5">No users found</td></tr>';
    return;
  }
  
  tbody.innerHTML = users.map(user => {
    const name = user.role === 'student' ? user.full_name : user.company_name;
    return `
      <tr>
        <td>${name || 'N/A'}</td>
        <td>${user.email}</td>
        <td>${user.role}</td>
        <td>${user.is_approved ? 'Yes' : 'No'}</td>
        <td>
          ${!user.is_approved ? `<a href="#" class="btn" onclick="approveUser('${user.id}'); return false;">Approve</a>` : ''}
          <a href="#" class="btn-grey" onclick="removeUser('${user.id}'); return false;">Remove</a>
        </td>
      </tr>
    `;
  }).join('');
}

async function approveUser(userId) {
  const { error } = await supabaseClient
      .from('users')
      .update({ is_approved: true })
    .eq('id', userId);
  
  if (error) {
    alert(error.message);
  } else {
    alert('User approved');
    loadUsers();
  }
}

async function removeUser(userId) {
  if (!confirm('Are you sure you want to remove this user?')) return;
  
  // Note: This requires admin privileges in Supabase
  const { error } = await supabaseClient
      .from('users')
      .delete()
    .eq('id', userId);
  
  if (error) {
    alert(error.message);
  } else {
    alert('User removed');
    loadUsers();
  }
}

async function loadAdminTasks() {
  await checkAuth();
  
  const { data: tasks, error } = await supabaseClient
    .from('tasks')
    .select('*, company:users(company_name)')
    .order('posted_at', { ascending: false });
  
  const tbody = document.getElementById('tasks-list');
  if (error || !tasks || tasks.length === 0) {
    tbody.innerHTML = '<tr><td colspan="5">No tasks found</td></tr>';
    return;
  }
  
  tbody.innerHTML = tasks.map(task => `
    <tr>
      <td>${task.title}</td>
      <td>${task.company?.company_name || 'N/A'}</td>
      <td>${task.payment_amount} BDT</td>
      <td><span class="status-${task.status}">${task.status}</span></td>
      <td><a href="#" class="btn-grey" onclick="deleteTask(${task.id}); return false;">Delete</a></td>
    </tr>
  `).join('');
}

async function deleteTask(taskId) {
  if (!confirm('Are you sure you want to delete this task?')) return;
  
  const { error } = await supabaseClient
      .from('tasks')
      .delete()
    .eq('id', taskId);
  
  if (error) {
    alert(error.message);
  } else {
    alert('Task deleted');
    loadAdminTasks();
  }
}

async function loadReports() {
  await checkAuth();
  
  // Overview stats
  const { data: users } = await supabaseClient.from('users').select('role');
  const { data: tasks } = await supabaseClient.from('tasks').select('status');
  const { data: apps } = await supabaseClient.from('applications').select('status');
  const { data: certs } = await supabaseClient.from('certificates').select('id');
  const { data: payments } = await supabaseClient.from('payments').select('amount, status');
  
  const totalUsers = users?.length || 0;
  const students = users?.filter(u => u.role === 'student').length || 0;
  const companies = users?.filter(u => u.role === 'company').length || 0;
  const totalTasks = tasks?.length || 0;
  const totalApps = apps?.length || 0;
  const totalCerts = certs?.length || 0;
  const totalPayments = payments?.filter(p => p.status === 'completed').reduce((sum, p) => sum + p.amount, 0) || 0;
  
  document.getElementById('report-stats').innerHTML = `
    <tr><td>Total Users</td><td>${totalUsers}</td></tr>
    <tr><td>Students</td><td>${students}</td></tr>
    <tr><td>Companies</td><td>${companies}</td></tr>
    <tr><td>Total Tasks</td><td>${totalTasks}</td></tr>
    <tr><td>Total Applications</td><td>${totalApps}</td></tr>
    <tr><td>Total Certificates</td><td>${totalCerts}</td></tr>
    <tr><td>Total Payments (BDT)</td><td>${totalPayments}</td></tr>
  `;
  
  // Tasks by status
  const taskStatusCounts = {};
  tasks?.forEach(t => { taskStatusCounts[t.status] = (taskStatusCounts[t.status] || 0) + 1; });
  
  document.getElementById('tasks-by-status').innerHTML = Object.entries(taskStatusCounts)
    .map(([status, count]) => `<tr><td>${status}</td><td>${count}</td></tr>`)
    .join('') || '<tr><td colspan="2">No data</td></tr>';
  
  // Applications by status
  const appStatusCounts = {};
  apps?.forEach(a => { appStatusCounts[a.status] = (appStatusCounts[a.status] || 0) + 1; });
  
  document.getElementById('applications-by-status').innerHTML = Object.entries(appStatusCounts)
    .map(([status, count]) => `<tr><td>${status}</td><td>${count}</td></tr>`)
    .join('') || '<tr><td colspan="2">No data</td></tr>';
}
