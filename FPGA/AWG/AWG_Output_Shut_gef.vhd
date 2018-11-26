----------------------------------------------------------------------------------
-- Company: Hatlab
-- Author: Chao Zhou
-- Create Date: 09/01/2018

----------------------------------------------------------------------------------
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use ieee.numeric_std.all;
USE IEEE.STD_LOGIC_unsigned.ALL;

entity AWGout_Shut_gef is
	port(
		trig_0   : in std_logic;
		trig_1   : in std_logic;
		clk200 : in std_logic;
		rst    : in std_logic;
		
		ef_start : in std_logic_vector(15 downto 0);
		ef_span      : in std_logic_vector(15 downto 0);
		ge_start : in std_logic_vector(15 downto 0);
		ge_span      : in std_logic_vector(15 downto 0);
		
		
		Din_sdi_dataStreamFCx5_S_data_0 : in std_logic_vector(15 downto 0);
		Din_sdi_dataStreamFCx5_S_data_1 : in std_logic_vector(15 downto 0);
		Din_sdi_dataStreamFCx5_S_data_2 : in std_logic_vector(15 downto 0);
		Din_sdi_dataStreamFCx5_S_data_3 : in std_logic_vector(15 downto 0);
		Din_sdi_dataStreamFCx5_S_data_4 : in std_logic_vector(15 downto 0);
		Din_sdi_dataStreamFCx5_S_valid  : in std_logic;
		
		Dout_sdi_dataStreamFCx5_M_data_0 : out std_logic_vector(15 downto 0);
		Dout_sdi_dataStreamFCx5_M_data_1 : out std_logic_vector(15 downto 0);
		Dout_sdi_dataStreamFCx5_M_data_2 : out std_logic_vector(15 downto 0);
		Dout_sdi_dataStreamFCx5_M_data_3 : out std_logic_vector(15 downto 0);
		Dout_sdi_dataStreamFCx5_M_data_4 : out std_logic_vector(15 downto 0);
		Dout_sdi_dataStreamFCx5_M_valid  : out std_logic
	);
end AWGout_Shut_gef;

architecture fpga of AWGout_Shut_gef is

  signal count: integer := 0;
  
begin
  
  process(rst,clk200,trig_0,trig_1)
  begin
	if rst='1' then
		count <= 0;
		Dout_sdi_dataStreamFCx5_M_data_0 <= (others => '0');
		Dout_sdi_dataStreamFCx5_M_data_1 <= (others => '0');
		Dout_sdi_dataStreamFCx5_M_data_2 <= (others => '0');
		Dout_sdi_dataStreamFCx5_M_data_3 <= (others => '0');
		Dout_sdi_dataStreamFCx5_M_data_4 <= (others => '0');
		Dout_sdi_dataStreamFCx5_M_valid  <='0';
	else
		if(clk200'event and clk200 = '1') then
			if trig_1 = '1' then   --f state or noise
				count <= 0;
				Dout_sdi_dataStreamFCx5_M_data_0 <= Din_sdi_dataStreamFCx5_S_data_0;
				Dout_sdi_dataStreamFCx5_M_data_1 <= Din_sdi_dataStreamFCx5_S_data_1;
				Dout_sdi_dataStreamFCx5_M_data_2 <= Din_sdi_dataStreamFCx5_S_data_2;
				Dout_sdi_dataStreamFCx5_M_data_3 <= Din_sdi_dataStreamFCx5_S_data_3;
				Dout_sdi_dataStreamFCx5_M_data_4 <= Din_sdi_dataStreamFCx5_S_data_4;
				Dout_sdi_dataStreamFCx5_M_valid  <= Din_sdi_dataStreamFCx5_S_valid;
				
			elsif trig_0 = '1' and trig_1 = '0' then   --e state
				count <= count + 1 ;
				if count < to_integer(unsigned(ef_start)) then
					Dout_sdi_dataStreamFCx5_M_data_0 <= Din_sdi_dataStreamFCx5_S_data_0;
					Dout_sdi_dataStreamFCx5_M_data_1 <= Din_sdi_dataStreamFCx5_S_data_1;
					Dout_sdi_dataStreamFCx5_M_data_2 <= Din_sdi_dataStreamFCx5_S_data_2;
					Dout_sdi_dataStreamFCx5_M_data_3 <= Din_sdi_dataStreamFCx5_S_data_3;
					Dout_sdi_dataStreamFCx5_M_data_4 <= Din_sdi_dataStreamFCx5_S_data_4;
					Dout_sdi_dataStreamFCx5_M_valid  <= Din_sdi_dataStreamFCx5_S_valid;
				elsif count < to_integer(unsigned(ef_start+ef_span)) then 
					Dout_sdi_dataStreamFCx5_M_data_0 <= "0000000000000000";
					Dout_sdi_dataStreamFCx5_M_data_1 <= "0000000000000001";
					Dout_sdi_dataStreamFCx5_M_data_2 <= "0000000000000000";
					Dout_sdi_dataStreamFCx5_M_data_3 <= "1111111111111111";
					Dout_sdi_dataStreamFCx5_M_data_4 <= "0000000000000000";
					Dout_sdi_dataStreamFCx5_M_valid  <= Din_sdi_dataStreamFCx5_S_valid;
				else
					Dout_sdi_dataStreamFCx5_M_data_0 <= Din_sdi_dataStreamFCx5_S_data_0;
					Dout_sdi_dataStreamFCx5_M_data_1 <= Din_sdi_dataStreamFCx5_S_data_1;
					Dout_sdi_dataStreamFCx5_M_data_2 <= Din_sdi_dataStreamFCx5_S_data_2;
					Dout_sdi_dataStreamFCx5_M_data_3 <= Din_sdi_dataStreamFCx5_S_data_3;
					Dout_sdi_dataStreamFCx5_M_data_4 <= Din_sdi_dataStreamFCx5_S_data_4;
					Dout_sdi_dataStreamFCx5_M_valid  <= Din_sdi_dataStreamFCx5_S_valid;
				end if;
			elsif trig_0 = '0' and trig_1 = '0' then   --g state
				count <= count + 1 ;
				if count < to_integer(unsigned(ef_start)) then
					Dout_sdi_dataStreamFCx5_M_data_0 <= Din_sdi_dataStreamFCx5_S_data_0;
					Dout_sdi_dataStreamFCx5_M_data_1 <= Din_sdi_dataStreamFCx5_S_data_1;
					Dout_sdi_dataStreamFCx5_M_data_2 <= Din_sdi_dataStreamFCx5_S_data_2;
					Dout_sdi_dataStreamFCx5_M_data_3 <= Din_sdi_dataStreamFCx5_S_data_3;
					Dout_sdi_dataStreamFCx5_M_data_4 <= Din_sdi_dataStreamFCx5_S_data_4;
					Dout_sdi_dataStreamFCx5_M_valid  <= Din_sdi_dataStreamFCx5_S_valid;
				elsif count < to_integer(unsigned(ge_start+ge_span)) then 
					Dout_sdi_dataStreamFCx5_M_data_0 <= "0000000000000000";
					Dout_sdi_dataStreamFCx5_M_data_1 <= "0000000000000001";
					Dout_sdi_dataStreamFCx5_M_data_2 <= "0000000000000000";
					Dout_sdi_dataStreamFCx5_M_data_3 <= "1111111111111111";
					Dout_sdi_dataStreamFCx5_M_data_4 <= "0000000000000000";
					Dout_sdi_dataStreamFCx5_M_valid  <= Din_sdi_dataStreamFCx5_S_valid;
				else
					Dout_sdi_dataStreamFCx5_M_data_0 <= Din_sdi_dataStreamFCx5_S_data_0;
					Dout_sdi_dataStreamFCx5_M_data_1 <= Din_sdi_dataStreamFCx5_S_data_1;
					Dout_sdi_dataStreamFCx5_M_data_2 <= Din_sdi_dataStreamFCx5_S_data_2;
					Dout_sdi_dataStreamFCx5_M_data_3 <= Din_sdi_dataStreamFCx5_S_data_3;
					Dout_sdi_dataStreamFCx5_M_data_4 <= Din_sdi_dataStreamFCx5_S_data_4;
					Dout_sdi_dataStreamFCx5_M_valid  <= Din_sdi_dataStreamFCx5_S_valid;
				end if;
			end if;
		end if;
	end if;
  end process;
end fpga;