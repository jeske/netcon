<?cs include:"header.cs" ?>

<?cs if:!?Query.incident_id ?>
<?cs include:"actinclist.cs" ?>
<p>
<?cs /if ?>

<?cs if:Query.incident_id ?>

<?cs with:inc = CGI.incident ?>

<table width=98%>
<form method=post action="index.py">
<input type=hidden name="incident_id" value="<?cs var:Query.incident_id ?>">
<tr><td valign=top>
<b>Incident <?cs var:inc.incident_id ?></b> (4 hours old)<br>
<table border=1>
<tr <?cs if:!?inc.name ?>BGCOLOR=#FFCCCC<?cs /if ?>><td align=right><b>Name</b></td>  
    <td><input size=30 style="width:200;" type=text name="inc_name" value="<?cs var:html_escape(inc.name) ?>"></td></tr>
<tr><td valign=top align=right><b>State</b></td>
 <td>
<?cs if:inc.state.enum == "new" ?>
   <input name=newstate value=_stay_ checked type=radio>Leave New<br>
   <input name=newstate value=ack type=radio>Acknowledge<br>
<?cs /if ?>
<?cs if:inc.state.enum == "viewed" ?>
   <input name=newstate value=_stay_ checked type=radio>Leave Viewed<br>
   <input name=newstate value=ack type=radio>Acknowledge<br>
<?cs /if ?>
<?cs if:inc.state.enum == "ack" ?>
   <input name=newstate value=_stay_ checked type=radio>Leave Acknowledged<br><?cs /if ?>
<?cs if:inc.state.enum == "watched" ?>
   <input name=newstate value=_stay_ checked type=radio>Leave Watched<br>
   <input name=newstate value=ack type=radio>Clear watch<br>
<?cs /if ?>
<?cs if:inc.state.enum != "watched" ?>
   <input name=newstate value=watched type=radio>Watch/Suppress
  <?cs if:0 ?>
     For 
     <select name=>
       <option>30 min
       <option>1 hour
       <option>2 hours
       <option>4 hours
       <option>1 week
     </select>
  <?cs /if ?>
  <br>
<?cs /if ?>
<?cs if:inc.state.enum != "resolved" ?>
   <input name=newstate value=watched type=radio>Resolve (include note!)
<?cs /if ?>
  </td></tr>
<tr><Td colspan=2 align=center>
<textarea style="width:100%;" cols=30 rows=2></textarea>
</td></tr>   
   
<tr><td colspan=2 align=center bgcolor=#eeeeee>
   <input type=submit name="Action.SaveInfo" value="Save"></td></tr>
    </tr>
</table>
</form>

</td><td valign=top align=right>
<?cs if:?CGI.active_incidents.0.incident_id ?>
<b>Active Incidents</b><br>
<table border=1>
  <tr><td>Incident</td><td>First Event</td></tr>
  <?cs each:ainc = CGI.active_incidents ?>
  <tr <?cs if:ainc.incident_id==Query.incident_id ?>BGCOLOR=#FFCCCC<?cs /if ?>>
      <td align=center><a href="index.py?incident_id=<?cs var:ainc.incident_id ?>">&nbsp;<?cs var:ainc.incident_id ?>&nbsp;</a></td>
      <td><?cs var:ainc.start.string ?></td>
  </tr>

  <?cs /each ?>
</table>

<a href="index.py">show all</a>
<?cs /if ?>

</td></tr></table>

<?cs if:CGI.incnotes.0.text ?>
<p><b>Notes</b><br>
<table border=1>
 <?cs each:note=CGI.incnotes ?>
   <tr><Td><?cs var:note.text ?></td></tr>A
 <?cs /each ?>
</table>

<?cs /if ?>

<p>


<p>
<b>Errors for Incident <?cs var:inc.incident_id ?></b>
<table border=1>
<form method=post action="index.py">
<input type=hidden name="incident_id" value="<?cs var:Query.incident_id ?>">
  <tr><td colspan=9 bgcolor=#eeeeee>
   Move selected to:
   <SELECT style="width:150" name="move_dest">
     <option value="new">New Incident
     <?cs each:inc=CGI.active_incidents ?>
      <?cs if:inc.incident_id != Query.incident_id ?>
       <option value="<?cs var:inc.incident_id ?>"><?cs var:inc.incident_id ?> - <?cs var:inc.name ?>
      <?cs /if ?>
     <?cs /each ?>
   </SELECT>
   <input type="submit" name="Action.MoveTo" value="Move">
  </td></tr>

  <?cs each:ierr=inc.errors ?>
    <tr>
      <td bgcolor=#eeeeee><input type=checkbox name="mverr.<?cs var:ierr.incident_error_map_id ?>" value="1"></td>
      <td><?cs var:ierr.incident_error_map_id ?></td>
      <td><?cs if:ierr.tdata.value=="1.0" ?><font color=red>err</font><?cs else ?><font color=green>ok</font><?cs /if ?>
      <td><?cs var:ierr.trigger.level ?></td>
      <td><b><?cs var:ierr.trigger.name ?></b></td>
      <td><?cs var:CGI.machines[ierr.source.source_mach_id].name ?></td>
      <td><?cs var:ierr.source.source_name ?></td>
      <td><?cs var:ierr.cdata.value ?></td>
      <td>
<img style="border:1px solid black;" width=100 height=50
     src="graphDataHistory.py?width=100&height=50&serv_id=<?cs var:ierr.cdata.serv_id ?>&source_id=<?cs var:ierr.cdata.source_id ?>">

<a href="viewDataHistory.py?serv_id=<?cs var:ierr.cdata.serv_id ?>&source_id=<?cs var:ierr.cdata.source_id ?>">history</a></td>
    </tr>
  <?cs /each ?>
</table>

</form>
<?cs /with ?>

<?cs else ?>

<hr>

<?cs include:"overview.cs" ?>

<?cs /if ?>





<?cs include:"footer.cs" ?>
