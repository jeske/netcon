<?cs include:"header.cs" ?>

viewService

<table border=1>
<?cs each:src=CGI.sources ?>
 <tr>
  <td><a href="viewDataHistory.py?serv_id=<?cs var:CGI.service.serv_id ?>&source_id=<?cs var:src.source_id ?>">history</a></td>
  <td><?cs var:src.machine.name ?></td>
  <td><?cs var:src.source_name ?></td>
 </tr>
<?cs /each ?>
</table>