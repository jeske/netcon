<?cs include:"header.cs" ?>

<p>
<b>viewService '<?cs var:CGI.service.namepath ?>:<?cs var:CGI.service.type ?>'</b><br>

<table border=1>
<?cs each:cdata=CGI.cdata ?>
  <tr>
   <td><a href="viewMachine.py?mach_id=<?cs var:CGI.sources[cdata.source_id].source_mach_id ?>"><?cs var:CGI.sources[cdata.source_id].machine.name ?></A></td>
   <td><?cs var:CGI.sources[cdata.source_id].source_name ?></td>
   <td><?cs var:cdata.value ?></td>
   <td>
<a href="viewDataHistory.py?serv_id=<?cs var:CGI.service.serv_id ?>&source_id=<?cs var:cdata.source_id ?>">
<img style="border:1px solid black;" width=100 height=50
     src="graphDataHistory.py?width=100&height=50&serv_id=<?cs var:CGI.service.serv_id ?>&source_id=<?cs var:cdata.source_id ?>">history
</a>
</td></tr>
<?cs /each ?>
</table>
