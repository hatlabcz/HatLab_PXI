----------------------------------------------------------------------------------
-- Company: Hatlab@Pitt
-- Author : Chao Zhou
-- Reference : slice by Marcel Gozalbo@Signadyne
-- Create Date: 07/18/2018
-- Description : Based on the origional Slice block that comes with Keysight M3602A.
--               The only difference is that here we can decide the slice start bit from the input port(instead of in the Generic) 

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

-- Uncomment the following library declaration if using
-- arithmetic functions with Signed or Unsigned values
use IEEE.NUMERIC_STD.ALL;

-- Uncomment the following library declaration if instantiating
-- any Xilinx primitives in this code.
--library UNISIM;
--use UNISIM.VComponents.all;

entity Slice_16 is	
	Generic (
		bus_in_width : integer := 32
	);
	
	Port (
		Din       : in std_logic_vector(bus_in_width-1 downto 0);
		Start_Bit : in std_logic_vector(4 downto 0);
		Dout      : out std_logic_vector(15 downto 0)
	);
	
end Slice_16;

architecture Behavioral of Slice_16 is

begin
	
	Dout <= Din(to_integer(unsigned(Start_Bit)) downto to_integer(unsigned(Start_Bit))-15);

end Behavioral;
