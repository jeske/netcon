<?cs include:"header.cs" ?>

<?cs if:?CGI.active_incidents.0.incident_id ?>
<table border=1>
  <tr><td>Incident</td><td>First Event</td><td>Last Event</td></tr>
  <?cs each:inc = CGI.active_incidents ?>
  <tr><td><?cs var:inc.incident_id ?></td>
      <td><?cs var:inc.start.string ?></td>
      <td><?cs var:inc.end.string ?></td>
  </tr>
  <?cs /each ?>
</table>

<?cs each:inc = CGI.active_incidents ?>
<p>
<b>Errors for Incident <?cs var:inc.incident_id ?></b>
<table border=1>
  <?cs each:ierr=inc.errors ?>
    <tr><td><?cs var:ierr.error_spec ?></td></tr>
  <?cs /each ?>
</table>

<?cs /each ?>

<?cs /if ?>

<p>
<b>Machines</b>
<table border=1>
  <tr><td>ID</td><td>name</td></tr>
<?cs each:m=CGI.machines ?>
  <Tr><td><a href="viewMachine.py?mach_id=<?cs var:m.mach_id ?>">&nbsp;<?cs var:m.mach_id ?>&nbsp;</a></td><td><?cs var:m.name ?></td></tr>
<?cs /each ?>

</table>



<?cs include:"footer.cs" ?>