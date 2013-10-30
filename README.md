PrintViaEmail
=============

Script to print email attachments automatically<br><br>

Program flow:<br><ul>
  <li>checkMail.py -> imports mailHandler<br></li>
  <li>mailHandler checks email account and returns with a list of emails along with attachments<br></li>
  <li>control returns to checkMail<br></li>
  <li>checkMail calls printJob which processes the detached attachments directory<br></li>
  <li>checkMail emails the user to inform them the job was processed</li></ul>
