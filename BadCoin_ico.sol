
// version of the compiler
pragma solidity >=0.7.0 <0.9.0;

contract badCoin_ico {
    // Introducing the number of had coins avaialable for sealed
    uint public max_badcoins = 1000000;
    
    // Introducing the USD to badcoin conversion 
    
    uint public usd_to_badcoins = 1000 ; 
    
    // Inroducing the number of badcoins that have been invested by the investors
    
    uint public total_badcoins_bought = 0;
    
    // Mapping from the investor address to its equity in badcoins and usd
    // it consist of array having address of every index and which points out the equity that a person is having in terms of usd and badcoins
    
    mapping(address=>uint) equity_badcoins;
    mapping(address=>uint) equity_usd;

    //checking weather a person can buy badcoins at any point of time
    
    modifier can_buy_badcoins(uint usd_invested){   //this function takes the argument of the total number of usd the invested want to invest
        
        require(usd_invested*usd_to_badcoins + total_badcoins_bought <= max_badcoins);
        _; // underscore here means that the function linked to the modifier will only execute if the require consition is satisfied
    }
    
    
    // Getting the equity in badcoins of an investor
    
    function equity_in_badcoins(address investor) external  returns (uint){
        return equity_badcoins[investor];
    }
    
    //Getting the equity in USD of an investor
      function equity_in_usd(address investor) external returns (uint){
        return equity_usd[investor];
    }
    
    
    //buying badcoins
    function buy_badcoins(address investor, uint usd_invested) external
    // mapping is used first to check weather a person  can buy badcoins or not
   
    can_buy_badcoins(usd_invested){
        uint badcoins_bought = usd_invested*usd_to_badcoins;
        equity_badcoins[investor]+= badcoins_bought;
        equity_usd[investor] = equity_badcoins[investor]/1000;
        total_badcoins_bought += badcoins_bought;
        
    }
    
    // Selling badcoins
    
      function sell_badcoins(address investor, uint badcoins_sold) external{
        
        equity_badcoins[investor]-= badcoins_sold;
        equity_usd[investor] = equity_badcoins[investor]/1000;
        total_badcoins_bought -= badcoins_sold;
        
    }

    
}