<?cs if:?CGI.active_incidents.0.incident_id ?>
<b>Active Incidents</b><br>
<table border=1>
  <tr><td>Incident</td><td>State</td><td>First Event</td><td>Last Change</td><td>Name</td></tr>
  <?cs each:inc = CGI.active_incidents ?>
  <tr <?cs if:inc.incident_id==Query.incident_id ?>BGCOLOR=#FFCCCC<?cs /if ?>>
      <td align=center><a href="index.py?incident_id=<?cs var:inc.incident_id ?>">&nbsp;<?cs var:inc.incident_id ?>&nbsp;</a></td>
      <td><?cs var:IncidentStates[inc.state.enum] ?></td>
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
