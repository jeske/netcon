<?cs include:"header.cs" ?>

<b><?cs if:CGI.create ?>Create New Trigger<?cs else ?>Edit Trigger '<?cs var:CGI.trigger.name ?>'<?cs /if ?></b><p>

<form action="./admin_edit_trigger.py" method=post>
<input type=hidden name="trigger_id" value="<?cs var:CGI.trigger.trigger_id ?>">
<input type=hidden name="role_id" value="<?cs var:CGI.role_id ?>">

<table align=center>

<tr><td>

<table>
<tr><td align=right><b>Name</b></td>
    <td><input type=text name=name size=30
          value="<?cs var:html_escape(CGI.trigger.name) ?>"></td></tr>
<tr><Td valign=top align=right><b>Service</b></td>
    <td><select name=serv_id size=12>
 <?cs each:serv=CGI.services ?>
   <option <?cs if:serv.serv_id == CGI.trigger.serv_id ?>SELECTED<?cs /if ?> value="<?cs var:serv.serv_id ?>"><?cs var:serv.namepath ?>:<?cs var:serv.type ?>
 <?cs /each ?>
 </select>
</td></tr>
</table>


</td><td valign=top>

If reported value is 
<select name="test_type">
<?cs each:tt=TestTypes ?>
 <option <?cs if:name(tt) == CGI.trigger.test_type ?>SELECTED<?cs /if ?> value="<?cs var:name(tt) ?>"><?cs var:html_escape(tt) ?>
<?cs /each ?>
</select>

<p>

...to the value <input type=text size=9 name=tvalue value="<?cs var:CGI.trigger.tvalue ?>">

<p>

...and the source matches regex 
<input type=text size=9 name=source_pattern value="<?cs var:html_escape(CGI.trigger.source_pattern) ?>">

<p>

...then trigger an event of severity 
<select name="level">
<?cs each:lvl=Levels ?>
 <option <?cs if:lvl == CGI.trigger.level ?>SELECTED<?cs /if ?> value="<?cs var:lvl ?>"><?cs var:lvl ?>
<?cs /each ?>
</select>

</td></tr>

<tr><Td bgcolor=#eeeeee colspan=2 align=center>
<a href="./admin_role.py?role_id=<?cs var:CGI.role_id ?>">&lt;&lt; Cancel</a> &nbsp; &nbsp; 
<?cs if:CGI.create ?>
  <input type=hidden name=create value=1>
  <input default type=submit name="Action.Save" value="Create &gt;&gt;">
<?cs else ?>
  <input default type=submit name="Action.Save" value="Save &gt;&gt;">
<?cs /if ?>
</td></tr>
</table>

</form>

<?cs include:"footer.cs" ?>
