----------------------------------------------------------------------------------
-- Company: Hatlab@Pitt
-- Author : Chao Zhou
-- Reference : Integrator_datax5 - Behavioral by Marcel Gozalbo@Signadyne
-- Create Date: 07/19/2018
-- Description : Based on the origional Integration block that comes with Keysight M3602A.
--               Here, the output is set to 32 bits 
--               And the integration start and end cycle can be set from the input.
--               The clr(rst) port is usually connected to the HVI trigger for reset of the counter
-------------------------------------------------------------------------
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.STD_LOGIC_unsigned.ALL;

-- Uncomment the following library declaration if using
-- arithmetic functions with Signed or Unsigned values
use IEEE.NUMERIC_STD.ALL;

-- Uncomment the following library declaration if instantiating
-- any Xilinx primitives in this code.
--library UNISIM;
--use UNISIM.VComponents.all;


-------------------------------------------------------------------------output is always 32 bits---------------------------------------------------------------------------------------------------------

entity Integrator_v3 is	
	Generic (
		input_width : integer := 16;
		input_signed : boolean := TRUE;
		input_latch	: boolean := FALSE
	);
	
	Port (
		start_point   : in std_logic_vector(15 downto 0);
		end_point     : in std_logic_vector(15 downto 0);
		
		Din : in std_logic_vector(input_width-1 downto 0);
		Dout : out std_logic_vector(31 downto 0):= (others => '0');
		clk : in std_logic;
		rst : in std_logic;
		clr:	in std_logic
	);
	
end Integrator_v3;

architecture Behavioral of Integrator_v3 is

signal Dout_int :	std_logic_vector(31 downto 0):= (others => '0');

signal Din_int :	std_logic_vector(input_width-1 downto 0);
signal count   :    integer := 0; 

begin

latch_in:	if(input_latch = TRUE) generate

				process(clk)
				begin	
					if(clk'event and clk = '1') then
						Din_int <= Din;
					end if;
				end process;
				
			end generate latch_in;
			
no_latch_in:	if(input_latch = FALSE) generate
				
					Din_int <= Din;
					
				end generate no_latch_in;
	

signed_in:	if(input_signed = TRUE) generate

				process(clk)
		  	    variable Dout_int :	std_logic_vector(31 downto 0):=(others=>'0');
			    begin	
			   	    if(rst = '1' or clr = '1') then
					    Dout_int := (others => '0');
						Dout <= (others => '0');
						count <= 0;		
					else
						if(clk'event and clk = '1') then
							if count = to_integer(signed(start_point)) then
								Dout_int := ((31 downto input_width => Din_int(input_width-1))&Din_int);
								count<=count+1;
								
							elsif count = to_integer(signed(end_point)) then
								Dout <= Dout_int;
								count <= count+1;
								
							else 
								count <= count+1;
								Dout_int := Dout_int+ 
											((31 downto input_width => Din_int(input_width-1))&Din_int);
								    
							end if;
						end if;
					end if;
				end process;
				
			end generate signed_in;
			
no_signed_in:	if(input_signed = FALSE) generate
	
					process(clk)
					variable Dout_int :	std_logic_vector(31 downto 0):=(others=>'0');
					begin	
						if(rst = '1' or clr = '1') then
							Dout_int := (others => '0');
							Dout <= (others => '0');
							count <= 0;
						else
							if(clk'event and clk = '1') then
								if count = to_integer(signed(start_point)) then
									Dout_int := ((31 downto input_width => '0')&Din_int);
									count<=count+1;
								
								elsif count = to_integer(signed(end_point)) then
									Dout <= Dout_int;
									count<=count+1;
								
								else 
									count <= count+1;
									Dout_int := Dout_int+ 
												((31 downto input_width => '0')&Din_int);
									    
								end if;
							end if;
						end if;
					end process;
					
				end generate no_signed_in;
				
	
end Behavioral;
