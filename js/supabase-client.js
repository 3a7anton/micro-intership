// Supabase configuration - QuickHire Project
const SUPABASE_URL = 'https://cnexjwkuraaqhcpzqzkx.supabase.co';
const SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNuZXhqd2t1cmFhcWdocHpxemt4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzU0NTgwMjQsImV4cCI6MjA5MTAzNDAyNH0.1rSZpT7yelZPavRtxSZZYKxWj87XKlbzkeBOuuKKQ5c';

const { createClient } = supabase;
const supabaseClient = createClient(SUPABASE_URL, SUPABASE_KEY);
