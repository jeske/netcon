
<?cs include:"header.cs" ?>

<p>
Data for Machine &nbsp; <b><?cs var:CGI.machine.name ?></b>

<p>
<?cs each:agent = CGI.agents ?>
Collected By <?cs var:agent.mach_id.name ?><p>

<table border=1>
<?cs each:srv=agent.services ?>
<tr><td><?cs var:CGI.services[srv.serv_id].namepath ?> - <?cs var:CGI.services[srv.serv_id].type ?></td>
<td>
  <table width=100%>
  <?cs each:src = srv.sources ?>
   <tr><td><?cs var:src.source_name ?></td>
       <td align=right><?cs each:st=src.states ?><?cs var:st.value ?><?cs /each ?></td>
   </tr>
  <?cs /each ?>
  </table>
</td>
</tr>
<?cs /each ?>
</table>

<?cs /each ?>


<?cs include:"footer.cs" ?>
