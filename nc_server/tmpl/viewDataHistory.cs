<?cs include:"header.cs" ?>

<b>view data for <?cs var:CGI.service.namepath ?>:<?cs var:CGI.service.type ?> 
@ <?cs var:CGI.source.machine.name ?>:<?cs var:CGI.source.source_name ?></b>

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
