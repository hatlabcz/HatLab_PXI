----------------------------------------------------------------------------------
-- Company: Hatlab@Pitt
-- Author: Chao Zhou
-- Create Date: 09/05/2018
-- Description : Based on the four input distance, judge which state the Qubit is in.
--               I,Q input is used to judge whether the signal is noise or not(threshold)
--               
----------------------------------------------------------------------------------
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.STD_LOGIC_unsigned.ALL;
use ieee.numeric_std.all;


entity IQ_Judge_Dist is 
  port(
    I : in std_logic_vector(15 downto 0);
	Q : in std_logic_vector(15 downto 0);
	
	num_of_state : in std_logic_vector(2 downto 0);         --maximun 4 states
	
	dist_g    : in std_logic_vector(15 downto 0);
	dist_e    : in std_logic_vector(15 downto 0);
	dist_f    : in std_logic_vector(15 downto 0);
	dist_h    : in std_logic_vector(15 downto 0);

	
	rst : in std_logic;
	clk : in std_logic;
	
	out_0 : out std_logic := '0';  
	out_1 : out std_logic := '0'     --00 for g, 01 for e, 10 for f, 11 for h (also used for noise)
  );
end IQ_Judge_Dist;


architecture fpga of IQ_Judge_Dist is

begin

	process(rst,clk)
	variable eg : std_logic_vector(15 downto 0):="0000000000000000";
	variable hf : std_logic_vector(15 downto 0):="0000000000000000";
	variable min_eg : std_logic_vector(15 downto 0):="0000000000000000";
	variable min_hf : std_logic_vector(15 downto 0):="0000000000000000";
	variable min_feg : std_logic_vector(15 downto 0):="0000000000000000";
	variable min    : std_logic_vector(15 downto 0):="0000000000000000";
	begin
		if rst='1' then
			out_0   <= '0';
			out_1   <= '0';
			eg :="0000000000000000";
			hf :="0000000000000000";
			min_eg :="0000000000000000";
			min_hf :="0000000000000000";
			min :="0000000000000000";
		else
			if(clk'event and clk = '1') then
				if (to_integer(signed(I))>1 or to_integer(signed(I))<-1) or (to_integer(signed(Q))>1 or to_integer(signed(Q))<-1) then
					eg:=dist_e+not dist_g+1;
					hf:=dist_h+not dist_f+1;
					if eg(15)='0' then 
						min_eg:= dist_g;
					else
						min_eg:= dist_e;
					end if;
					if hf(15)='0' then 
						min_hf:= dist_f;
					else
						min_hf:= dist_h;
					end if;
					min:=min_hf+ not min_eg+1;
					
					min_feg:=dist_f+ not min_eg+1;
					
					if(num_of_state = "100") then
						if min(15)='0' and eg(15)='0' then
							out_0<='0';
							out_1<='0';
						elsif min(15)='0' and eg(15)='1' then
							out_0<='1';
							out_1<='0';
						elsif min(15)='1' and hf(15)='0' then
							out_0<='0';
							out_1<='1';
						elsif min(15)='1' and hf(15)='1' then
							out_0<='1';
							out_1<='1';
						end if;
					
					elsif(num_of_state = "011") then
						if min_feg(15)='0' and eg(15)='0' then
							out_0<='0';
							out_1<='0';
						elsif min_feg(15)='0' and eg(15)='1' then
							out_0<='1';
							out_1<='0';
						elsif min_feg(15)='1' then
							out_0<='0';
							out_1<='1';
						end if;
						
					elsif(num_of_state = "010") then
						if eg(15)='0' then 
							out_0<='0';
							out_1<='0';
						else
							out_0<='1';
							out_1<='0';
						end if;
					
					end if;
				else 
					out_0   <= '1';
					out_1   <= '1';
				end if;
			end if;
		end if;		
	  end process;
			

end fpga;
