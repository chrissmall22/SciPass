<SciPass>

   <switch dpid="0000000000000001">
    <domain name="R&amp;E" mode="SciDMZ" admin_status="active" least_specific_prefix_len="24" most_specific_prefix_len="32" 
	    blacklist_priority="1000" whitelist_priority="900" sensor_min_load_threshold="0.1" sensor_load_delta_threshold="0.1"
	    max_prefixes="200" idle_timeout="90" hard_timeout="300" >

      <port of_port_id="1" type="lan" name="foo8" description="lan int">
        <prefix type="v4">10.0.17.0/24</prefix>
        <prefix type="v4">10.0.18.0/24</prefix>
      </port>

      <port of_port_id="2" type="lan" name="foo12" description="another lan int">
	<prefix type="v4">10.0.19.0/24</prefix>
        <prefix type="v4">10.0.20.0/24</prefix>
      </port>
      

     <!-- this is my main wan port -->
     <port of_port_id="3" type="wan" name="foo8" description="wan int" />


     <sensor_port of_port_id="4" bw="10G" sensor_id="sensor1" admin_status="active" description="some host"/>
     <sensor_port of_port_id="5" bw="10G" sensor_id="sensor2" admin_status="active" description="some host"/>
     <sensor_port of_port_id="6" bw="10G" sensor_id="sensor3" admin_status="disabled" description="some host" />
     <sensor_port of_port_id="7" bw="10G" sensor_id="sensor4" admin_status="spare" description="some host" />

   </domain>
  </switch>

</SciPass>
