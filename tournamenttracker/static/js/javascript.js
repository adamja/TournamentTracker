
function selectAllCheckboxes(checkboxName, activate) {
  checkboxes = document.getElementsByName(checkboxName);
  console.log(checkboxName, activate)
  for(var i=0, n=checkboxes.length;i<n;i++) {
    checkboxes[i].checked = activate;
  }
}