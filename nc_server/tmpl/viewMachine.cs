
<?cs include:"header.cs" ?>

<p>
Data for Machine &nbsp; <b><?cs var:CGI.machine.name ?></b>
<?cs if:Query.images ?>
  <a href="./viewMachine.py?mach_id=<?cs var:url_escape(Query.mach_id) ?>">Remove images</a>
<?cs else ?>
  <a href="./viewMachine.py?mach_id=<?cs var:url_escape(Query.mach_id) ?>&images=1">Add images</a>
<?cs /if ?>

<p>
<?cs each:agent = CGI.agents ?>
<p>
Collected By <a href="./viewMachine.py?mach_id=<?cs var:agent.mach_id ?>"><?cs var:agent.mach_id.name ?></a><br>

<table border=1>
<?cs each:srv=agent.services ?>
  <?cs set:triggered = 0 ?>
  <?cs each:src = srv.sources ?>
    <?cs if:src.state.value.triggered ?>
      <?cs set:triggered = 1 ?>
    <?cs /if ?>
  <?cs /each ?>
  <?cs if:CGI.services[srv.serv_id].namepath.trigger_id ?>
    <?cs with:trigger_id = CGI.services[srv.serv_id].namepath.trigger_id ?>
    <?cs if:CGI.triggers[trigger_id].trigger_id ?>
    <?cs with:trigger = CGI.triggers[trigger_id] ?>
    <?cs if:trigger.level == "info" ?>
      <?cs set:trigger_bgcolor = "bgcolor=yellow" ?>
    <?cs elif:trigger.level == "warning" ?>
      <?cs set:trigger_bgcolor = "bgcolor=yellow" ?>
    <?cs else ?>
      <?cs set:trigger_bgcolor = "bgcolor=red" ?>
    <?cs /if ?>
    <tr><td valign=top <?cs if:triggered ?><?cs var:trigger_bgcolor ?><?cs /if ?>>
    &nbsp;&nbsp;<?cs var:trigger.name ?>
    <?cs if:CGI.services[srv.serv_id].type == "state" ?>
      <?cs var:TestTypes[trigger.test_type] ?> <?cs var:trigger.tvalue ?>
    <?cs else ?>
      <?cs var:TestTypes[trigger.test_type] ?> <?cs var:trigger.tvalue ?> in
      <?cs var:trigger.trend_config.time ?> <?cs var:TrendUnits[trigger.trend_config.unit].name ?>
    <?cs /if ?>
    <?cs /with ?>
    <?cs else ?>
      <tr><td>&nbsp;&nbsp;no trigger found? serv_id:<?cs var:srv.serv_id ?> trigger_id:<?cs var:trigger_id ?>
    <?cs /if ?>
    <?cs /with ?>
  <?cs else ?>
    <tr><td>
    <?cs set:trigger_bgcolor = "" ?>
    <?cs var:CGI.services[srv.serv_id].namepath ?> - <?cs var:CGI.services[srv.serv_id].type ?>
  <?cs /if ?>
  </td>
  <td>
    <table width=100% cellspacing=0>
    <?cs each:src = srv.sources ?>
     <tr <?cs if:src.state.value.triggered ?><?cs var:trigger_bgcolor ?><?cs /if ?>><td><?cs var:src.source_name ?></td>
	 <td align=right><?cs var:src.state.value ?></td>
	 <td width=1% align=right nowrap>&nbsp;
  <a href="viewDataHistory.py?serv_id=<?cs var:srv.serv_id ?>&source_id=<?cs var:src.source_id ?>">
  	<?cs if:Query.images ?>
	   <img style="border:1px solid black;" width=40 height=10
		src="graphDataHistory.py?width=40&height=10&serv_id=<?cs var:srv.serv_id ?>&source_id=<?cs var:src.source_id ?>">
	   <?cs else ?>
	     history
	   <?cs /if ?>
	  </a></td>
     </tr>
    <?cs /each ?>
    </table>
  </td>
  </tr>
<?cs /each ?>
</table>

<?cs /each ?>


<?cs include:"footer.cs" ?>
