<?cs include:"header.cs" ?>

<?cs if:?CGI.active_incidents.0.incident_id ?>
<table border=1>
  <tr><td>Incident</td><td>First Event</td><td>Last Event</td></tr>
  <?cs each:inc = CGI.active_incidents ?>
  <tr><td><?cs var:inc.incident_id ?></td>
      <td><?cs var:inc.start.string ?></td>
      <td><?cs var:inc.end.string ?></td>
      <td><a href="index.py?clear_incident=<?cs var:inc.incident_id ?>">Clear</a></td>
  </tr>

  <?cs /each ?>
</table>

<?cs each:inc = CGI.active_incidents ?>
<p>
<b>Errors for Incident <?cs var:inc.incident_id ?></b>
<table border=1>
  <?cs each:ierr=inc.errors ?>
    <tr>
      <td><?cs var:ierr.incident_error_map_id ?></td>
      <td><?cs if:ierr.tdata.value=="1.0" ?><font color=red>err</font><?cs else ?><font color=green>ok</font><?cs /if ?>
      <td><?cs var:ierr.trigger.level ?></td>
      <td><b><?cs var:ierr.trigger.name ?></b></td>
      <td><?cs var:CGI.machines[ierr.source.source_mach_id].name ?></td>
      <td><?cs var:ierr.source.source_name ?></td>
      <td><?cs var:ierr.cdata.value ?></td>
      <td><a href="viewDataHistory.py?serv_id=<?cs var:ierr.cdata.serv_id ?>&source_id=<?cs var:ierr.cdata.source_id ?>">history</a></td>
    </tr>
  <?cs /each ?>
</table>

<?cs /each ?>

<?cs /if ?>

<p>
<hr>

<table>
<tr>
<td valign=top>

<b>Machines</b>
<table border=1>
  <tr><td>ID</td><td>name</td></tr>
<?cs each:m=CGI.machines ?>
  <Tr><td><a href="viewMachine.py?mach_id=<?cs var:m.mach_id ?>">&nbsp;<?cs var:m.mach_id ?>&nbsp;</a></td><td><?cs var:m.name ?></td></tr>
<?cs /each ?>

</table>

</td><td valign=top>
<b>Agents</b>
<table border=1>
<tr><td>ID</td><td>name</td></tr>
<?cs each:agent=CGI.agents ?>
<tr><td><?cs var:agent.agent_id ?></td>
  <td><?cs var:CGI.machines[agent.mach_id].name ?></td></tr>
<?cs /each ?>
</table>

</td><td valign=top>

<b>Services</b><br>
<table border=1>
<?cs each:srv=CGI.show_services ?>
 <tr>
  <td align=center><a href="viewService.py?serv_id=<?cs var:srv.serv_id ?>"><?cs var:srv.serv_id ?></a></td>
  <td><?cs var:srv.namepath ?>:<?cs var:srv.type ?></td></tr>
<?cs /each ?>
</table>

</td></tr></table>



<?cs include:"footer.cs" ?>
