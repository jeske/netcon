
<?cs include:"header.cs" ?>

<p>
Data for Machine &nbsp; <b><?cs var:CGI.machine.name ?></b>

<p>
<?cs each:agent = CGI.agents ?>
<p>
Collected By <?cs var:agent.mach_id.name ?><br>

<table border=1>
<?cs each:srv=agent.services ?>
<tr><td><?cs var:CGI.services[srv.serv_id].namepath ?> - <?cs var:CGI.services[srv.serv_id].type ?></td>
<td>
  <table width=100%>
  <?cs each:src = srv.sources ?>
   <tr><td><?cs var:src.source_name ?></td>
       <td align=right><?cs each:st=src.states ?><?cs var:st.value ?><?cs /each ?></td>
       <td width=1% align=right><a href="viewDataHistory.py?serv_id=<?cs var:srv.serv_id ?>&source_id=<?cs var:src.source_id ?>">history</a></td>
   </tr>
  <?cs /each ?>
  </table>
</td>
</tr>
<?cs /each ?>
</table>

<?cs /each ?>


<?cs include:"footer.cs" ?>
