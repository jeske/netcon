<?cs if:?CGI.active_incidents.0.incident_id ?>
<b>Active Incidents</b><br>
<table border=1>
  <tr><td>Incident</td><td>State</td><td colspan=2>Cur</td><td>First Event</td><td>Last Change</td><td>Name</td></tr>
  <?cs each:inc = CGI.active_incidents ?>
  <tr>
      <td align=center><a href="index.py?incident_id=<?cs var:inc.incident_id ?>">&nbsp;<?cs var:inc.incident_id ?>&nbsp;</a></td>
      <td <?cs if:(inc.state.enum=="new") || (inc.state.enum=="viewed") ?>BGCOLOR=#FFCCCC<?cs /if ?>><?cs var:IncidentStates[inc.state.enum] ?></td>
      <td align=right><?cs if:inc.good_count ?><b style="color:green"><?cs var:inc.good_count ?></b><?cs else ?>&nbsp;<?cs /if ?></td>
      <Td align=left><?cs if:inc.bad_count ?><b style="color:red"><?cs var:inc.bad_count ?><?cs else ?>&nbsp;<?cs /if ?></td>
      <td><?cs var:inc.start.string ?></td>
      <td><?cs var:inc.end.string ?></td>
      <td><b><?cs var:inc.name ?></b></td>
  </tr>

  <?cs /each ?>
</table>

<?cs else ?>
  <center><i>No active incidents</i></center>
<?cs /if ?>

<p>
