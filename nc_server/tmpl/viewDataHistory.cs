<?cs include:"header.cs" ?>

<b>view data for <?cs var:CGI.service.namepath ?>:<?cs var:CGI.service.type ?> 
@ <?cs var:CGI.source.machine.name ?>:<?cs var:CGI.source.source_name ?></b>

<p>
<img style="border:1px solid black;" src="graphDataHistory.py?serv_id=<?cs var:CGI.service.serv_id ?>&source_id=<?cs var:CGI.source.source_id ?>">

<p>
<table border=1>
<?cs each:hd=CGI.history ?>
 <tr>
  <td><?cs var:hd.pstart.string ?></td>
  <td><?cs var:hd.pend.string ?></td>
  <td><?cs var:hd.value ?></td>
 </tr>
<?cs /each ?>
</table>
