// Settings page interactions: panel toggle, pane switch, basic handlers
document.addEventListener('DOMContentLoaded', function(){
  // Open panel when Account & Security card clicked
  const acctCard = document.getElementById('card-account-security');
  const panel = document.getElementById('panel-account-security');
  if(acctCard){
    // Navigate to a dedicated account settings page when the card is clicked
    acctCard.addEventListener('click', ()=>{
      window.location.href = '/settings/account';
    });
    // keep inline panel hidden by default if present
    if(panel){
      panel.style.display = 'none';
      panel.setAttribute('aria-hidden','true');
    }
  }

  // Custom avatar upload: trigger hidden file input and preview
  const avatarInput = document.getElementById('account-avatar');
  const changeAvatarBtn = document.getElementById('change-avatar-btn');
  const avatarPreview = document.getElementById('avatar-preview');
  if(changeAvatarBtn && avatarInput){
    changeAvatarBtn.addEventListener('click', ()=> avatarInput.click());
    avatarInput.addEventListener('change', ()=>{
      const f = avatarInput.files && avatarInput.files[0];
      if(!f) return;
      const reader = new FileReader();
      reader.onload = (e)=>{ if(avatarPreview) avatarPreview.src = e.target.result; };
      reader.readAsDataURL(f);
    });
  }

  // Switch component for 2FA
  const tfaToggle = document.getElementById('tfa-toggle');
  const tfaSwitch = document.getElementById('tfa-switch');
  if(tfaSwitch){
    tfaSwitch.addEventListener('click', ()=>{
      tfaSwitch.classList.toggle('on');
      if(tfaToggle) tfaToggle.checked = tfaSwitch.classList.contains('on');
    });
  }

  // Loading state for update buttons
  function buttonLoading(btn){
    btn.classList.add('loading');
    btn.setAttribute('aria-busy','true');
  }
  function buttonDone(btn){
    btn.classList.remove('loading');
    btn.removeAttribute('aria-busy');
  }

  document.getElementById('update-profile')?.addEventListener('click', (e)=>{
    const b = e.currentTarget;
    buttonLoading(b);
    // simulate async save
    setTimeout(()=>{ buttonDone(b); alert('Profil mis à jour (simulation).'); }, 900);
  });
  document.getElementById('change-password')?.addEventListener('click', (e)=>{
    const b = e.currentTarget;
    const newp = document.getElementById('new-password').value;
    const conf = document.getElementById('confirm-password').value;
    if(newp !== conf){ alert('New password and confirmation do not match.'); return; }
    buttonLoading(b);
    setTimeout(()=>{ buttonDone(b); alert('Mot de passe changé (simulation).'); }, 900);
  });

  // Panel menu switching
  const menuItems = document.querySelectorAll('.panel-menu li');
  menuItems.forEach(item => item.addEventListener('click', ()=>{
    menuItems.forEach(i=>i.classList.remove('active'));
    item.classList.add('active');
    const pane = item.dataset.pane;
    document.querySelectorAll('.pane').forEach(p=>p.classList.add('hidden'));
    const show = document.getElementById('pane-'+pane);
    if(show) show.classList.remove('hidden');
  }));

  // Theme toggle
  // Theme toggle with persistence
  const themeInputs = document.querySelectorAll('input[name="theme"]');
  function applyTheme(name){
    if(name === 'dark') document.documentElement.classList.add('theme-dark');
    else document.documentElement.classList.remove('theme-dark');
  }
  // initialize from localStorage
  const saved = localStorage.getItem('theme');
  if(saved) applyTheme(saved);
  // set radio state if present
  if(themeInputs && themeInputs.length){
    themeInputs.forEach(r=>{
      if(r.value === saved) r.checked = true;
      r.addEventListener('change', (e)=>{
        applyTheme(e.target.value);
        try{ localStorage.setItem('theme', e.target.value); }catch(e){}
      });
    });
  }

  // (Profile/password handlers with loading are defined above)

  document.getElementById('export-data')?.addEventListener('click', ()=>{
    alert('Export started (stub).');
  });
  document.getElementById('download-backup')?.addEventListener('click', ()=>{
    alert('Backup download started (stub).');
  });

  // Import file input
  const importFile = document.getElementById('import-file');
  const uploadBtn = document.querySelector('.btn.upload');
  if(uploadBtn && importFile){
    uploadBtn.addEventListener('click', ()=> importFile.click());
    importFile.addEventListener('change', ()=>{
      if(importFile.files.length) alert('File selected: '+importFile.files[0].name+' (stub)');
    });
  }

  // Global save buttons for settings pages
  const saveBtns = document.querySelectorAll('.save-settings-btn');
  saveBtns.forEach(btn => btn.addEventListener('click', (e)=>{
    const b = e.currentTarget;
    buttonLoading(b);
    // TODO: replace with real POST/fetch to save settings
    setTimeout(()=>{
      buttonDone(b);
      // small success UI
      alert('Paramètres enregistrés (simulation).');
    }, 900);
  }));

});
