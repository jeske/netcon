<?cs include:"header.cs" ?>

<b>view data for :
<br>
<?cs each:_ds=CGI.dataset ?><?cs var:_ds.service.namepath ?>:<?cs var:_ds.service.type ?> 
@ <?cs var:_ds.source.machine.name ?>:<?cs var:_ds.source.source_name ?><br>
<?cs /each ?>
</b>

<p>
<img style="border:1px solid black;" src="graphDataHistory2.py?<?cs each:_ds=CGI.dataset ?>serv_id=<?cs var:_ds.service.serv_id ?>&source_id=<?cs var:_ds.source.source_id ?>&<?cs /each ?>">

<table>
<tr>
<?cs each:_ds=CGI.dataset ?>
<td valign=top>
<table border=0>
<tr><td align=center colspan=3><?cs var:_ds.service.namepath ?>:<?cs var:_ds.service.type ?></td></tr>
<tr><td>Start</td><td>End</td><td>Value</td></tr>
  <?cs each:_hd=_ds.history ?>
   <tr>
    <td><font size=-3><?cs var:_hd.pstart.string ?></font></td>
    <td><font size=-3><?cs var:_hd.pend.string ?></td>
    <td><font size=-3><?cs var:_hd.value ?></td>
   </tr>
  <?cs /each ?>
</table>
</td>
<?cs /each ?>
</tr></table>

