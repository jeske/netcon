<table>
<tr>
<td valign=top>

<b>Machines</b>
<table border=1>
  <tr><td align=center>ID</td><td>name</td></tr>
<?cs each:m=CGI.machines ?>
  <Tr><td align=center><a href="viewMachine.py?mach_id=<?cs var:m.mach_id ?>">&nbsp;<?cs var:m.mach_id ?>&nbsp;</a></td><td><?cs var:m.name ?></td></tr>
<?cs /each ?>

</table>

</td><td valign=top>
<b>Agents</b>
<table border=1>
<tr><td>ID</td><td>name</td></tr>
<?cs each:agent=CGI.agents ?>
<tr><td><?cs var:agent.agent_id ?></td>
  <td><?cs var:CGI.machines[agent.mach_id].name ?>
   <?cs if:agent.last_check_in == 0 ?>
    <font color=red>no check in data</font>
   <?cs elif:(CGI.CurrentTime - agent.last_check_in) > (60*10) ?>
    <font color=red><?cs var:(CGI.CurrentTime - agent.last_check_in) / 60 ?> minutes old</font>
   <?cs /if ?>
  </td></tr>
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

