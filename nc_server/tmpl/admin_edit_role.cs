<?cs include:"header.cs" ?>

<b>Edit role</b>

<form action="admin_edit_role.py" method=post>
<?cs if:CGI.create ?>
  <input type=hidden name=create value="1">
<?cs else ?>
  <input type=hidden name=role_id value="<?cs var:CGI.role.role_id ?>">
<?cs /if ?>

<table>
<tr><td align=right><b>Name</b></td>
    <td><input type=text name=name value="<?cs var:html_escape(CGI.role.name) ?>">
</tr>

<tr><td bgcolor=#eeeeee colspan=2 align=center>
<input type=submit name="Action.Save" value="Save &gt;&gt;">
</td></tr>
</table>

</form>

<?cs include:"footer.cs" ?>