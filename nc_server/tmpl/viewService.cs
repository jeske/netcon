<?cs include:"header.cs" ?>

viewService

<table border=1>
<?cs each:src=CGI.sources ?>
 <tr>
  <td><?cs var:src.machine.name ?></td>
  <td><?cs var:src.source_name ?></td>
  <td><a href="viewDataHistory.py?serv_id=<?cs var:CGI.service.serv_id ?>&source_id=<?cs var:src.source_id ?>">
<img style="border:1px solid black;" width=100 height=50
     src="graphDataHistory.py?width=100&height=50&serv_id=<?cs var:CGI.service.serv_id ?>&source_id=<?cs var:src.source_id ?>">history
</a></td>
 </tr>
<?cs /each ?>
</table>