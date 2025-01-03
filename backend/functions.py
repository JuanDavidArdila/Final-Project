import math as m
import CoolProp.CoolProp as CP
from geopy.distance import geodesic
from sqlalchemy import func
from config import app, db 
from models import BlueBuilding, RedBuilding, FixedData, BRBuildingsm, BlueBuildingDistance, Cluster, Connecttions,Hot_Temperatures,Cold_Temperatures
import heapq
def TforheatingInside(T_inf,T_i,L,v_dot,Di,Thicknessp,Thickness_i, k_tub, Emiss, k_r):
    Tfin = T_inf
    Temperatures=[x / 10000 for x in range(int(T_inf*10000), int(T_i*10000))]                   #Temperature at the exit [°C]
    maxdelta_Q=10000000000
    A_c1=(1/4) * m.pi* (Di**2)                                                     #Cross sectional area of the internal pipe [m2]
    V_avg=v_dot/A_c1                                                               #Mean velocity of water [m/s]
    Do=Di+(2*Thicknessp)                                                               #Diameter without the insulation 
    D_r=Do+(2*Thickness_i)                                                             #Total diameter of the pipe
    Asi=m.pi*Di*L                                                                  #Total internal area of the pipe [m2]
    A_r=m.pi*D_r*L                                                                 #Total external area of the pipe [m2]
    R_pipe=m.log(Do / Di, m.e) / (2 * k_tub*m.pi*L)                                #Conductive thermal resistance of the pipe [K/W]                                   
    R_insul=m.log(D_r / Do, m.e) / (2 * k_r*m.pi*L)                                #Conductive thermal resistance of the insulation [K/W]
    R_tot=R_pipe+R_insul                                                           #Total conductive thermal resistance [K/W]
    for T_e in Temperatures:
        T_bulk=(T_i+T_e)/2                                                         #Bulk Temperature [°C]
        T_bulk_k=T_bulk+273.15                                                     #Bulk Temperature [°K]
        rho_water=CP.PropsSI('D', 'T', T_bulk_k, 'P', 101335, 'Water')             #Density of water at Bulk Temperature [kg/m3]
        m_dot=rho_water*v_dot                                                      #Mass flow rate of the water [kg/s]
        Cp=CP.PropsSI('C', 'T', T_bulk_k, 'P', 101335, 'Water')                    #Specific heat capacity [J/kg.K]
        Q_dot=m_dot*Cp*(T_i-T_e)                                                   #Heat loss of the water [W]
        q_f=Q_dot/Asi                                                              #Total forced convection throughout inside of the pipe [W/m2]
        Pr_water=CP.PropsSI('PRANDTL', 'T', T_bulk_k, 'P', 101330, 'Water')        #Prandtl of water at Bulk Temperature
        k_water = CP.PropsSI('L', 'T', T_bulk_k, 'P', 101330, 'Water')             #Conductivity of water [W/m.K]
        miu_water = CP.PropsSI('V', 'T', T_bulk_k, 'P', 101330, 'Water')           #Dynamic viscocity of water [kg/m.s]
        kinematic_water = miu_water / rho_water                                    #Kinematic viscocity of water [m2/s]
        Re = V_avg * Di / kinematic_water                                          #Reynolds number
        Nu_water = 0.023 * (Re**0.8) * (Pr_water**0.4)                             #Nusselt Number
        h_f= (k_water/ Di) * Nu_water                                              #Forced convection heat transfer coefficient [W/m2.K]
        Tsi_i=T_i-(q_f/h_f)                                                        #Inner surface temperature at the start of the pipe
        Tse_i=Tsi_i-(Q_dot*R_tot)                                                  #Outer surface temperature at the start of the pipe
        Tsi_e=T_e-(q_f/h_f)                                                        #Inner surface temperature at the end of the pipe
        Tse_e=Tsi_e-(Q_dot*R_tot)                                                  #Outer surface temperature at the end of the pipe
        if Tse_e>=T_inf:
            Tse_m=(Tse_i+Tse_e)/2
            T_film=(Tse_m+T_inf)/2
            T_film_k = T_film + 273
            Beta = 1 / T_film_k
            k_air = CP.PropsSI('L', 'T', T_film_k, 'P', 101330, 'Air')
            miu_air = CP.PropsSI('V', 'T', T_film_k, 'P', 101330, 'Air')
            Pr_air = CP.PropsSI('PRANDTL', 'T', T_film_k, 'P', 101330, 'Air')
            rho_air = CP.PropsSI('D', 'T', T_film_k, 'P', 101330, 'Air')
            kinematic_air = miu_air / rho_air
            Ra = 9.81 * Beta * (Tse_m - T_inf) * (Do**3) * Pr_air / kinematic_air
            Nu_air=(0.6+((0.387*(Ra**(1/6)))/((1+((0.539/Pr_air)**(9/16)))**(8/27))))**2
            h_natural = Nu_air * k_air / D_r
            Q_convn=A_r*h_natural*(Tse_m - T_inf)
            Q_rad=Emiss*A_r*(5.67*(10**-8))*(((Tse_m+273)**4)-((T_inf+273)**4))
            Q_tot=Q_convn+Q_rad
            delta_Q=abs(Q_tot-Q_dot)
            if delta_Q<maxdelta_Q:
                maxdelta_Q=delta_Q
                Tfin=T_e
    if Tfin is None:
        raise ValueError("Tfin was not properly calculated.")
    return Tfin

def TforheatingAir(T_inf,T_i,L,v_dot,Di,Thicknessp,Thickness_i, k_tub, Emiss, k_r, Air_velocity, irradiance):
    irradiance=irradiance*1000/24
    Tfin = T_inf
    Temperatures=[x / 10000 for x in range(int(T_inf*10000), int(T_i*10000))]                   #Temperature at the exit [°C]
    maxdelta_Q=10000000000
    A_c1=(1/4) * m.pi* (Di**2)                                                     #Cross sectional area of the internal pipe [m2]
    V_avg=v_dot/A_c1                                                               #Mean velocity of water [m/s]
    Do=Di+(2*Thicknessp)                                                               #Diameter without the insulation 
    D_r=Do+(2*Thickness_i)                                                             #Total diameter of the pipe
    Asi=m.pi*Di*L                                                                  #Total internal area of the pipe [m2]
    A_r=m.pi*D_r*L                                                                 #Total external area of the pipe [m2]
    R_pipe=m.log(Do / Di, m.e) / (2 * k_tub*m.pi*L)                                #Conductive thermal resistance of the pipe [K/W]                                   
    R_insul=m.log(D_r / Do, m.e) / (2 * k_r*m.pi*L)                                #Conductive thermal resistance of the insulation [K/W]
    R_tot=R_pipe+R_insul                                                           #Total conductive thermal resistance [K/W]
    for T_e in Temperatures:
        T_bulk=(T_i+T_e)/2                                                         #Bulk Temperature [°C]
        T_bulk_k=T_bulk+273.15                                                     #Bulk Temperature [°K]
        rho_water=CP.PropsSI('D', 'T', T_bulk_k, 'P', 101335, 'Water')             #Density of water at Bulk Temperature [kg/m3]
        m_dot=rho_water*v_dot                                                      #Mass flow rate of the water [kg/s]
        Cp=CP.PropsSI('C', 'T', T_bulk_k, 'P', 101335, 'Water')                    #Specific heat capacity [J/kg.K]
        Q_dot=m_dot*Cp*(T_i-T_e)                                                   #Heat loss of the water [W]
        q_f=Q_dot/Asi                                                              #Total forced convection throughout inside of the pipe [W/m2]
        Pr_water=CP.PropsSI('PRANDTL', 'T', T_bulk_k, 'P', 101330, 'Water')        #Prandtl of water at Bulk Temperature
        k_water = CP.PropsSI('L', 'T', T_bulk_k, 'P', 101330, 'Water')             #Conductivity of water [W/m.K]
        miu_water = CP.PropsSI('V', 'T', T_bulk_k, 'P', 101330, 'Water')           #Dynamic viscocity of water [kg/m.s]
        kinematic_water = miu_water / rho_water                                    #Kinematic viscocity of water [m2/s]
        Re1 = V_avg * Di / kinematic_water                                          #Reynolds number
        Nu_water = 0.023 * (Re1**0.8) * (Pr_water**0.4)                             #Nusselt Number
        h_f= (k_water/ Di) * Nu_water                                              #Forced convection heat transfer coefficient [W/m2.K]
        Tsi_i=T_i-(q_f/h_f)                                                        #Inner surface temperature at the start of the pipe
        Tse_i=Tsi_i-(Q_dot*R_tot)                                                  #Outer surface temperature at the start of the pipe
        Tsi_e=T_e-(q_f/h_f)                                                        #Inner surface temperature at the end of the pipe
        Tse_e=Tsi_e-(Q_dot*R_tot)                                                  #Outer surface temperature at the end of the pipe
        if Tse_e>=T_inf:
            Tse_m=(Tse_i+Tse_e)/2
            T_film=(Tse_m+T_inf)/2
            T_film_k = T_film + 273
            Beta = 1 / T_film_k
            k_air = CP.PropsSI('L', 'T', T_film_k, 'P', 101330, 'Air')
            miu_air = CP.PropsSI('V', 'T', T_film_k, 'P', 101330, 'Air')
            Pr_air = CP.PropsSI('PRANDTL', 'T', T_film_k, 'P', 101330, 'Air')
            rho_air = CP.PropsSI('D', 'T', T_film_k, 'P', 101330, 'Air')
            kinematic_air = miu_air / rho_air
            Re2=Air_velocity*D_r/kinematic_air
            Nu_air=0.3+(((0.62*(Re2**(1/2))*(Pr_air**(1/3)))/((1+(0.4/Pr_air)**2/3)**(1/4)))*(1+(Re2/282000)**(5/8))**(4/5))
            h_forzada = Nu_air * k_air / D_r
            Q_convf=A_r*h_forzada*(Tse_m - T_inf)
            Q_rad=Emiss*A_r*(5.67*(10**-8))*(((Tse_m+273)**4)-((T_inf+273)**4))
            Q_irad=irradiance*A_r/2
            Q_tot=Q_convf+Q_rad-Q_irad
            delta_Q=abs(Q_tot-Q_dot)
            if delta_Q<maxdelta_Q:
                maxdelta_Q=delta_Q
                Tfin=T_e
    if Tfin is None:
        raise ValueError("Tfin was not properly calculated.")
    
    return Tfin

def TforheatingGround(T_ground,T_i,L,v_dot,Di,Thicknessp,Thickness_i, k_tub,k_r):
    Tfin = T_ground
    Temperatures=[x / 10000 for x in range(int(T_ground*10000), int(T_i*10000))]                   #Temperature at the exit [°C]
    maxdelta_Q=10000000000
    A_c1=(1/4) * m.pi* (Di**2)                                                     #Cross sectional area of the internal pipe [m2]
    V_avg=v_dot/A_c1                                                               #Mean velocity of water [m/s]
    Do=Di+(2*Thicknessp)                                                               #Diameter without the insulation 
    D_r=Do+(2*Thickness_i)                                                             #Total diameter of the pipe
    Asi=m.pi*Di*L                                                                  #Total internal area of the pipe [m2]
    R_pipe=m.log(Do / Di, m.e) / (2 * k_tub*m.pi*L)                                #Conductive thermal resistance of the pipe [K/W]                                   
    R_insul=m.log(D_r / Do, m.e) / (2 * k_r*m.pi*L)                                #Conductive thermal resistance of the insulation [K/W]
    R_tot=R_pipe+R_insul                                                           #Total conductive thermal resistance [K/W]
    for T_e in Temperatures:
        T_bulk=(T_i+T_e)/2                                                         #Bulk Temperature [°C]
        T_bulk_k=T_bulk+273.15                                                     #Bulk Temperature [°K]
        rho_water=CP.PropsSI('D', 'T', T_bulk_k, 'P', 101335, 'Water')             #Density of water at Bulk Temperature [kg/m3]
        m_dot=rho_water*v_dot                                                      #Mass flow rate of the water [kg/s]
        Cp=CP.PropsSI('C', 'T', T_bulk_k, 'P', 101335, 'Water')                    #Specific heat capacity [J/kg.K]
        Q_dot=m_dot*Cp*(T_i-T_e)                                                   #Heat loss of the water [W]
        Pr_water=CP.PropsSI('PRANDTL', 'T', T_bulk_k, 'P', 101330, 'Water')        #Prandtl of water at Bulk Temperature
        k_water = CP.PropsSI('L', 'T', T_bulk_k, 'P', 101330, 'Water')             #Conductivity of water [W/m.K]
        miu_water = CP.PropsSI('V', 'T', T_bulk_k, 'P', 101330, 'Water')           #Dynamic viscocity of water [kg/m.s]
        kinematic_water = miu_water / rho_water                                    #Kinematic viscocity of water [m2/s]
        Re = V_avg * Di / kinematic_water                                          #Reynolds number
        Nu_water = 0.023 * (Re**0.8) * (Pr_water**0.4)                             #Nusselt Number
        h_f= (k_water/ Di) * Nu_water                                              #Forced convection heat transfer coefficient [W/m2.K]
        Tse=T_ground
        Tsi=Tse+(Q_dot*R_tot)
        if T_e>Tsi:
            LMTD=(T_i-T_e)/m.log(((Tsi-T_e)/(Tsi-T_i)), m.e)
            Q_tot=h_f*(Asi)*(abs(LMTD))
            delta_Q=abs(Q_tot-Q_dot)
            if delta_Q<maxdelta_Q:
                maxdelta_Q=delta_Q
                Tfin=T_e
    if Tfin is None:
        raise ValueError("Tfin was not properly calculated.")
    return Tfin

def TforcoolingInside(T_inf,T_i,L,v_dot,Di,Thicknessp,Thickness_i, k_tub, Emiss, k_r):
    Tfin = T_inf
    maxdelta_Q=100000000000
    Temperatures=[x / 10000 for x in range(int(T_i*10001), int(T_inf*10000))]                      #Temperature at the exit [°C]
    A_c1=(1/4) * m.pi* (Di**2)                                                     #Cross sectional area of the internal pipe [m2]
    V_avg=v_dot/A_c1                                                               #Mean velocity of water [m/s]
    Do=Di+(2*Thicknessp)                                                               #Diameter without the insulation 
    D_r=Do+(2*Thickness_i)                                                             #Total diameter of the pipe
    Asi=m.pi*Di*L                                                                  #Total internal area of the pipe [m2]
    A_r=m.pi*D_r*L                                                                 #Total external area of the pipe [m2]
    R_pipe=m.log(Do / Di, m.e) / (2 * k_tub*m.pi*L)                                #Conductive thermal resistance of the pipe [K/W]                                   
    R_insul=m.log(D_r / Do, m.e) / (2 * k_r*m.pi*L)                                #Conductive thermal resistance of the insulation [K/W]
    R_tot=R_pipe+R_insul                                                           #Total conductive thermal resistance [K/W]
    for T_e in Temperatures:
        T_bulk=(T_i+T_e)/2                                                         #Bulk Temperature [°C]
        T_bulk_k=T_bulk+273.15                                                     #Bulk Temperature [°K]
        rho_water=CP.PropsSI('D', 'T', T_bulk_k, 'P', 101335, 'Water')             #Density of water at Bulk Temperature [kg/m3]
        m_dot=rho_water*v_dot                                                      #Mass flow rate of the water [kg/s]
        Cp=CP.PropsSI('C', 'T', T_bulk_k, 'P', 101335, 'Water')                    #Specific heat capacity [J/kg.K]
        Q_dot=m_dot*Cp*(T_e-T_i)                                                   #Heat loss of the water [W]
        q_f=Q_dot/Asi                                                              #Total forced convection throughout inside of the pipe [W/m2]
        Pr_water=CP.PropsSI('PRANDTL', 'T', T_bulk_k, 'P', 101330, 'Water')        #Prandtl of water at Bulk Temperature
        k_water = CP.PropsSI('L', 'T', T_bulk_k, 'P', 101330, 'Water')             #Conductivity of water [W/m.K]
        miu_water = CP.PropsSI('V', 'T', T_bulk_k, 'P', 101330, 'Water')           #Dynamic viscocity of water [kg/m.s]
        kinematic_water = miu_water / rho_water                                    #Kinematic viscocity of water [m2/s]
        Re = V_avg * Di / kinematic_water                                          #Reynolds number
        Nu_water = 0.023 * (Re**0.8) * (Pr_water**0.3)                             #Nusselt Number
        h_f= (k_water/ Di) * Nu_water                                              #Forced convection heat transfer coefficient [W/m2.K]
        Tsi_i=T_i+(q_f/h_f)                                                        #Inner surface temperature at the start of the pipe
        Tse_i=Tsi_i+(Q_dot*R_tot)                                                  #Outer surface temperature at the start of the pipe
        Tsi_e=T_e+(q_f/h_f)                                                        #Inner surface temperature at the end of the pipe
        Tse_e=Tsi_e+(Q_dot*R_tot)                                                  #Outer surface temperature at the end of the pipe
        if Tse_e<=T_inf:
            Tse_m=(Tse_i+Tse_e)/2
            T_film=(Tse_m+T_inf)/2
            T_film_k = T_film + 273
            Beta = 1 / T_film_k
            k_air = CP.PropsSI('L', 'T', T_film_k, 'P', 101330, 'Air')
            miu_air = CP.PropsSI('V', 'T', T_film_k, 'P', 101330, 'Air')
            Pr_air = CP.PropsSI('PRANDTL', 'T', T_film_k, 'P', 101330, 'Air')
            rho_air = CP.PropsSI('D', 'T', T_film_k, 'P', 101330, 'Air')
            kinematic_air = miu_air / rho_air
            Ra = 9.81 * Beta * (T_inf-Tse_m) * (Do**3) * Pr_air / kinematic_air
            Nu_air=(0.6+((0.387*(Ra**(1/6)))/((1+((0.539/Pr_air)**(9/16)))**(8/27))))**2
            h_natural = Nu_air * k_air / D_r
            Q_convn=A_r*h_natural*(T_inf-Tse_m)
            Q_rad=Emiss*A_r*(5.67*(10**-8))*(((T_inf+273)**4)-((Tse_m+273)**4))
            Q_tot=Q_convn+Q_rad
            delta_Q=abs(Q_tot-Q_dot)
            if delta_Q<maxdelta_Q:
                maxdelta_Q=delta_Q
                Tfin=T_e
            else:
               break
    if Tfin is None:
        raise ValueError("Tfin was not properly calculated.")   
    return Tfin

def TforcoolingAir(T_inf,T_i,L,v_dot,Di,Thicknessp,Thickness_i, k_tub, Emiss, k_r, Air_velocity, irradiance):
    irradiance=irradiance*1000/24
    Tfin = 0
    maxdelta_Q=100000000000
    Temperatures=[x / 10000 for x in range(int(T_i*10001), int(T_inf*10000))]                   #Temperature at the exit [°C]
    A_c1=(1/4) * m.pi* (Di**2)                                                     #Cross sectional area of the internal pipe [m2]
    V_avg=v_dot/A_c1                                                               #Mean velocity of water [m/s]
    Do=Di+(2*Thicknessp)                                                               #Diameter without the insulation 
    D_r=Do+(2*Thickness_i)                                                             #Total diameter of the pipe
    Asi=m.pi*Di*L                                                                  #Total internal area of the pipe [m2]
    A_r=m.pi*D_r*L                                                                 #Total external area of the pipe [m2]
    R_pipe=m.log(Do / Di, m.e) / (2 * k_tub*m.pi*L)                                #Conductive thermal resistance of the pipe [K/W]                                   
    R_insul=m.log(D_r / Do, m.e) / (2 * k_r*m.pi*L)                                #Conductive thermal resistance of the insulation [K/W]
    R_tot=R_pipe+R_insul                                                           #Total conductive thermal resistance [K/W]
    for T_e in Temperatures:
        T_bulk=(T_i+T_e)/2                                                         #Bulk Temperature [°C]
        T_bulk_k=T_bulk+273.15                                                     #Bulk Temperature [°K]
        rho_water=CP.PropsSI('D', 'T', T_bulk_k, 'P', 101335, 'Water')             #Density of water at Bulk Temperature [kg/m3]
        m_dot=rho_water*v_dot                                                      #Mass flow rate of the water [kg/s]
        Cp=CP.PropsSI('C', 'T', T_bulk_k, 'P', 101335, 'Water')                    #Specific heat capacity [J/kg.K]
        Q_dot=m_dot*Cp*(T_e-T_i)                                                   #Heat loss of the water [W]
        q_f=Q_dot/Asi                                                              #Total forced convection throughout inside of the pipe [W/m2]
        Pr_water=CP.PropsSI('PRANDTL', 'T', T_bulk_k, 'P', 101330, 'Water')        #Prandtl of water at Bulk Temperature
        k_water = CP.PropsSI('L', 'T', T_bulk_k, 'P', 101330, 'Water')             #Conductivity of water [W/m.K]
        miu_water = CP.PropsSI('V', 'T', T_bulk_k, 'P', 101330, 'Water')           #Dynamic viscocity of water [kg/m.s]
        kinematic_water = miu_water / rho_water                                    #Kinematic viscocity of water [m2/s]
        Re1 = V_avg * Di / kinematic_water                                          #Reynolds number
        Nu_water = 0.023 * (Re1**0.8) * (Pr_water**0.3)                             #Nusselt Number
        h_f= (k_water/ Di) * Nu_water                                              #Forced convection heat transfer coefficient [W/m2.K]
        Tsi_i=T_i+(q_f/h_f)                                                        #Inner surface temperature at the start of the pipe
        Tse_i=Tsi_i+(Q_dot*R_tot)                                                  #Outer surface temperature at the start of the pipe
        Tsi_e=T_e+(q_f/h_f)                                                        #Inner surface temperature at the end of the pipe
        Tse_e=Tsi_e+(Q_dot*R_tot)                                                  #Outer surface temperature at the end of the pipe
        if Tse_e<=T_inf:
            Tse_m=(Tse_i+Tse_e)/2
            T_film=(Tse_m+T_inf)/2
            T_film_k = T_film + 273
            Beta = 1 / T_film_k
            k_air = CP.PropsSI('L', 'T', T_film_k, 'P', 101330, 'Air')
            miu_air = CP.PropsSI('V', 'T', T_film_k, 'P', 101330, 'Air')
            Pr_air = CP.PropsSI('PRANDTL', 'T', T_film_k, 'P', 101330, 'Air')
            rho_air = CP.PropsSI('D', 'T', T_film_k, 'P', 101330, 'Air')
            kinematic_air = miu_air / rho_air
            Re2=Air_velocity*D_r/kinematic_air
            Nu_air=0.3+(((0.62*(Re2**(1/2))*(Pr_air**(1/3)))/((1+(0.4/Pr_air)**2/3)**(1/4)))*(1+(Re2/282000)**(5/8))**(4/5))
            h_forzada = Nu_air * k_air / D_r
            Q_convf=A_r*h_forzada*(T_inf-Tse_m)
            Q_rad=0
            Q_irad=irradiance*A_r/2
            Q_tot=Q_convf+Q_rad+Q_irad
            delta_Q=abs(Q_tot-Q_dot)
            if delta_Q<maxdelta_Q:
                maxdelta_Q=delta_Q
                Tfin=T_e
    if Tfin is None:
        raise ValueError("Tfin was not properly calculated.")
    return Tfin

def TforcoolingGround(T_ground,T_i,L,v_dot,Di,Thicknessp,Thickness_i, k_tub,k_r):
    Tfin = T_ground
    Temperatures=[x / 10000 for x in range(int(T_i*10001), int(T_ground*10000))]                   #Temperature at the exit [°C]
    maxdelta_Q=10000000000
    A_c1=(1/4) * m.pi* (Di**2)                                                     #Cross sectional area of the internal pipe [m2]
    V_avg=v_dot/A_c1                                                               #Mean velocity of water [m/s]
    Do=Di+(2*Thicknessp)                                                               #Diameter without the insulation 
    D_r=Do+(2*Thickness_i)                                                             #Total diameter of the pipe
    Asi=m.pi*Di*L                                                                  #Total internal area of the pipe [m2]
    R_pipe=m.log(Do / Di, m.e) / (2 * k_tub*m.pi*L)                                #Conductive thermal resistance of the pipe [K/W]                                   
    R_insul=m.log(D_r / Do, m.e) / (2 * k_r*m.pi*L)                                #Conductive thermal resistance of the insulation [K/W]
    R_tot=R_pipe+R_insul                                                           #Total conductive thermal resistance [K/W]
    for T_e in Temperatures:
        T_bulk=(T_i+T_e)/2                                                         #Bulk Temperature [°C]
        T_bulk_k=T_bulk+273.15                                                     #Bulk Temperature [°K]
        rho_water=CP.PropsSI('D', 'T', T_bulk_k, 'P', 101335, 'Water')             #Density of water at Bulk Temperature [kg/m3]
        m_dot=rho_water*v_dot                                                      #Mass flow rate of the water [kg/s]
        Cp=CP.PropsSI('C', 'T', T_bulk_k, 'P', 101335, 'Water')                    #Specific heat capacity [J/kg.K]
        Q_dot=m_dot*Cp*(T_e-T_i)                                                   #Heat loss of the water [W]
        Pr_water=CP.PropsSI('PRANDTL', 'T', T_bulk_k, 'P', 101330, 'Water')        #Prandtl of water at Bulk Temperature
        k_water = CP.PropsSI('L', 'T', T_bulk_k, 'P', 101330, 'Water')             #Conductivity of water [W/m.K]
        miu_water = CP.PropsSI('V', 'T', T_bulk_k, 'P', 101330, 'Water')           #Dynamic viscocity of water [kg/m.s]
        kinematic_water = miu_water / rho_water                                    #Kinematic viscocity of water [m2/s]
        Re = V_avg * Di / kinematic_water                                          #Reynolds number
        Nu_water = 0.023 * (Re**0.8) * (Pr_water**0.3)                             #Nusselt Number
        h_f= (k_water/ Di) * Nu_water                                              #Forced convection heat transfer coefficient [W/m2.K]
        Tse=T_ground
        Tsi=Tse-(Q_dot*R_tot)
        if T_e<Tsi:
            LMTD=(T_i-T_e)/m.log(((Tsi-T_e)/(Tsi-T_i)), m.e)
            Q_tot=h_f*(Asi)*(abs(LMTD))
            delta_Q=abs(Q_tot-Q_dot)
            if delta_Q<maxdelta_Q:
                maxdelta_Q=delta_Q
                Tfin=T_e
    if Tfin is None:
        raise ValueError("Tfin was not properly calculated.")
    return Tfin

def calculate_and_store_distances():
    blue_buildings = BlueBuilding.query.all()
    red_buildings = RedBuilding.query.all()

    for blue1 in blue_buildings:
        for blue2 in blue_buildings:
            if blue1 != blue2:
                distance = geodesic((blue1.latitude, blue1.longitude), (blue2.latitude, blue2.longitude)).meters
                building_distance = BlueBuildingDistance(building1_id=blue1.buildingId, latitude1=blue1.latitude, longitude1=blue1.longitude, 
                                                         building2_id=blue2.buildingId, latitude2=blue2.latitude, longitude2=blue2.longitude, distance=distance)     ##Im working with with instances of SQLAlchemy model classes
                db.session.add(building_distance)

    # Iterate over each pair of buildings
    for blue_building in blue_buildings:
        for red_building in red_buildings:
            # Calculate distance between blue and red buildings
            distance = geodesic((blue_building.latitude, blue_building.longitude),(red_building.latitude, red_building.longitude)).meters

            # Store the distance in the database
            #building_distance = BuildingDistance(buildingb_id=blue_building.buildingId, buildingb_type=blue_building.type ,buildingr_id=red_building.buildingId, buildingr_type=red_building.type , distance=distance)
            blue_red = BRBuildingsm(bbuilding_id=blue_building.buildingId, blatitude=blue_building.latitude,blongitude=blue_building.longitude, 
                                   rbuilding_id=red_building.buildingId,rlatitude=red_building.latitude,rlongitude=red_building.longitude, distance=float(distance))
            #db.session.add(building_distance)
            db.session.add(blue_red)
    db.session.commit()
    # Commit the changes to the database
    
    
def clusters():
    # Fetch all existing building distances

    min_distances_query = (
    db.session.query(BRBuildingsm.bbuilding_id,BRBuildingsm.blatitude,BRBuildingsm.blongitude,
                     BRBuildingsm.rbuilding_id,BRBuildingsm.rlatitude,BRBuildingsm.rlongitude,
                     db.func.min(BRBuildingsm.distance))
    .group_by(BRBuildingsm.bbuilding_id).all()
    )

    for tuple in min_distances_query:
        rbuilding_id =tuple[3]
        rlatitude=tuple[4]
        rlongitude=tuple[5]
        bbuilding_id =tuple[0]
        blatitude=tuple[1]
        blongitude=tuple[2]
        distance =tuple[6]
        clusters=Cluster(rbuilding_id=rbuilding_id,rlatitude=rlatitude,rlongitude=rlongitude,
                         bbuilding_id=bbuilding_id,blatitude=blatitude,blongitude=blongitude,
                         distance=distance 
                         )
        
        db.session.add(clusters)
    db.session.commit()



def get_building_groups():
    building_groups = {}
    
    # Query Cluster table to get red building ids and their corresponding blue building distances
    clusters = Cluster.query.all()
    for cluster in clusters:
        red_building_id = cluster.rbuilding_id              #When i put it on a dictionary, for an unknown reason it converts to a string
        blue_building_id = cluster.bbuilding_id
        distance = cluster.distance
        
        # Initialize building group if not already present
        if red_building_id not in building_groups:
            building_groups[red_building_id] = {}
        
        # Add red building entry if not already present
        if red_building_id not in building_groups[red_building_id]:
            building_groups[red_building_id][red_building_id] = []

        # Add the distance from the red building to the blue building
        building_groups[red_building_id][red_building_id].append([distance, blue_building_id])
        
        # Add blue building distances to the building group
        if blue_building_id not in building_groups[red_building_id]:
            building_groups[red_building_id][blue_building_id] = []
        building_groups[red_building_id][blue_building_id].append([distance, red_building_id])

        #Building groups basically stores the distance of every building in the cluster with each other. Before this is only considered th red-blue distances
    
    # Query BlueBuildingDistance table to get distances between blue buildings within each group
    for red_building_id, group in building_groups.items():
        blue_building_ids = [b_id for b_id in group if b_id != red_building_id]
        if blue_building_ids:
            associated_blue_buildings = BlueBuildingDistance.query.filter(
                (BlueBuildingDistance.building1_id.in_(blue_building_ids)) &
                (BlueBuildingDistance.building2_id.in_(blue_building_ids))
            ).all()
            for distance_entry in associated_blue_buildings:
                building1_id = str(distance_entry.building1_id)                    #It does not recognize the key unless is a String
                building2_id = str(distance_entry.building2_id)
                distance = distance_entry.distance
                group[float(building1_id)].append([distance, float(building2_id)])
                #group[building2_id].append((distance, building1_id))
    total_distance=0
    overall_connections={}
    #The folloing is the Prim's algorithm
    for x in building_groups:
        N=len(building_groups[x])
        res=0
        visit=set()
        minH=[[0,x,-1]]
        connections=[]
        while len(visit) <N:
            cost, i, prev = heapq.heappop(minH)
            if i in visit:  #Maybe in here add the node on another list
                continue
            if prev != -1:  # Ignore the initial push with prev = -1
                connections.append([prev, i,cost])
            res += cost
            visit.add(i)
            for neiCost, nei in building_groups[x][i]:
                if nei not in visit:
                    heapq.heappush(minH, [neiCost,nei,i])
        overall_connections[x]=connections
        total_distance+=res

    added_connections = set()  # Set to track unique connections
    for mainbuilding_id in overall_connections:
        for elpepe in overall_connections[mainbuilding_id]:
            firstbuilding_id = float(elpepe[0])
            secondbuilding_id = float(elpepe[1])
            distance=float(elpepe[2])

            firstbuilding_type = "red" if firstbuilding_id == mainbuilding_id else "blue"
            secondbuilding_type = "red" if secondbuilding_id == mainbuilding_id else "blue"

            if firstbuilding_type == "blue":
                first_building = BlueBuilding.query.filter_by(buildingId=firstbuilding_id).first()
            else:
                first_building = RedBuilding.query.filter_by(buildingId=firstbuilding_id).first()
            
            firstbuilding_latitude = first_building.latitude
            firstbuilding_longitude = first_building.longitude

            # Fetch coordinates for the second building
            if secondbuilding_type == "blue":
                second_building = BlueBuilding.query.filter_by(buildingId=secondbuilding_id).first()
            else:
                second_building = RedBuilding.query.filter_by(buildingId=secondbuilding_id).first()

            secondbuilding_latitude = second_building.latitude
            secondbuilding_longitude = second_building.longitude

            # Ensure the connection is unique
            connection = tuple(sorted([firstbuilding_id, secondbuilding_id]))
            if connection not in added_connections:
                added_connections.add(connection)
                connect = Connecttions(
                    mainbuilding_id=float(mainbuilding_id),
                    firstbuilding_id=firstbuilding_id,
                    firstbuilding_type=firstbuilding_type,
                    firstbuilding_latitude=firstbuilding_latitude,
                    firstbuilding_longitude=firstbuilding_longitude,
                    secondbuilding_id=secondbuilding_id,
                    secondbuilding_type=secondbuilding_type,
                    secondbuilding_latitude=secondbuilding_latitude,
                    secondbuilding_longitude=secondbuilding_longitude,
                    distance=distance
                )
                db.session.add(connect)
    db.session.commit()

    return res



def hot_temperatures():
    fixed_data = FixedData.query.first()
    distances = Connecttions.query.all()
    internalDiameter = fixed_data.internalDiameter
    pipeThickness = fixed_data.pipeThickness
    pipeConductivity = fixed_data.pipeConductivity
    insulationThickness = fixed_data.insulationThickness
    insulationConductivity = fixed_data.insulationConductivity
    emissivity = fixed_data.emissivity
    ambientTemperature = fixed_data.ambientTemperature
    groundTemperature = fixed_data.groundTemperature
    airVelocity = fixed_data.airVelocity
    irradiance = fixed_data.irradiance

    visited = set()
    temperatures = {}
    connections = []
    translated_connections = {}
    coordinates = {}

    # Structuring connections
    for connection in distances:
        mainbuilding_id = connection.mainbuilding_id
        firstbuilding_id = connection.firstbuilding_id
        firstbuilding_type = connection.firstbuilding_type
        firstbuilding_latitude = connection.firstbuilding_latitude
        firstbuilding_longitude = connection.firstbuilding_longitude
        secondbuilding_id = connection.secondbuilding_id
        secondbuilding_type = connection.secondbuilding_type
        secondbuilding_latitude = connection.secondbuilding_latitude
        secondbuilding_longitude = connection.secondbuilding_longitude
        distance = connection.distance
        connections.append({
            "mainbuilding_id": mainbuilding_id,
            "firstbuilding_id": firstbuilding_id,
            "firstbuilding_type": firstbuilding_type,
            "firstbuilding_latitude": firstbuilding_latitude,
            "firstbuilding_longitude": firstbuilding_longitude,
            "secondbuilding_id": secondbuilding_id,
            "secondbuilding_type": secondbuilding_type,
            "secondbuilding_latitude": secondbuilding_latitude,
            "secondbuilding_longitude": secondbuilding_longitude,
            "distance": distance
        })

    for pair in connections:
        coordinates[pair["firstbuilding_id"]] = [pair["firstbuilding_latitude"], pair["firstbuilding_longitude"]]
        coordinates[pair["secondbuilding_id"]] = [pair["secondbuilding_latitude"], pair["secondbuilding_longitude"]]

    for pair in connections:
        if not pair["firstbuilding_id"] in translated_connections:
            translated_connections[pair["firstbuilding_id"]] = [[pair["secondbuilding_id"], pair["distance"]]]
        else:
            translated_connections[pair["firstbuilding_id"]].append([pair["secondbuilding_id"], pair["distance"]])

    def calculate_temperatures():
        # Queue for BFS
        queue = []

        # Initialize with red buildings
        for red_building in RedBuilding.query.all():
            exit_temperature = red_building.exitTemperature
            flow_rate = red_building.flowRate
            building_id = red_building.buildingId
            temperatures[building_id] = [0, exit_temperature]
            queue.append((building_id, exit_temperature, flow_rate))

        while queue:
            current_building, current_exit_temp, current_flow_rate = queue.pop(0)
            visited.add(current_building)

            for neighbor, distance in translated_connections.get(current_building, []):
                if neighbor not in visited:
                    type_of_connection = BlueBuilding.query.filter_by(buildingId=neighbor).first().connectionType
                    DeltaT = BlueBuilding.query.filter_by(buildingId=neighbor).first().DeltaT
                    if type_of_connection == "Ground":
                        entry_temp = TforheatingGround(groundTemperature, current_exit_temp, distance, current_flow_rate, internalDiameter, pipeThickness, insulationThickness, pipeConductivity, insulationConductivity)
                    elif type_of_connection == "Inside":
                        entry_temp = TforheatingInside(ambientTemperature, current_exit_temp, distance, current_flow_rate, internalDiameter, pipeThickness, insulationThickness, pipeConductivity, emissivity, insulationConductivity)
                    elif type_of_connection == "Air":
                        entry_temp = TforheatingAir(ambientTemperature, current_exit_temp, distance, current_flow_rate, internalDiameter, pipeThickness, insulationThickness, pipeConductivity, emissivity, insulationConductivity, airVelocity, irradiance)

                    outlet_temp = entry_temp - DeltaT
                    temperatures[neighbor] = [entry_temp, outlet_temp]

                    # Add the neighbor to the queue to process its neighbors
                    queue.append((neighbor, outlet_temp, current_flow_rate))

    calculate_temperatures()

    for building_id, temps in temperatures.items():
        entry_temperature = temps[0]
        exit_temperature = temps[1]
        latitude, longitude = coordinates.get(building_id, [0, 0])
        h_temp = Hot_Temperatures(
            building_id=building_id,
            building_latitude=latitude,
            building_longitude=longitude,
            inlet_temperature=entry_temperature,
            exit_temperature=exit_temperature
        )
        db.session.add(h_temp)
    
    db.session.commit()
    return temperatures, translated_connections,coordinates


def cold_temperatures():
    fixed_data = FixedData.query.first()
    distances = Connecttions.query.all()
    internalDiameter = fixed_data.internalDiameter
    pipeThickness = fixed_data.pipeThickness
    pipeConductivity = fixed_data.pipeConductivity
    insulationThickness = fixed_data.insulationThickness
    insulationConductivity = fixed_data.insulationConductivity
    emissivity = fixed_data.emissivity
    ambientTemperature = fixed_data.ambientTemperature
    groundTemperature = fixed_data.groundTemperature
    airVelocity = fixed_data.airVelocity
    irradiance = fixed_data.irradiance

    visited = set()
    temperatures = {}
    connections = []
    translated_connections = {}
    coordinates = {}

    # Structuring connections
    for connection in distances:
        mainbuilding_id = connection.mainbuilding_id
        firstbuilding_id = connection.firstbuilding_id
        firstbuilding_type = connection.firstbuilding_type
        firstbuilding_latitude = connection.firstbuilding_latitude
        firstbuilding_longitude = connection.firstbuilding_longitude
        secondbuilding_id = connection.secondbuilding_id
        secondbuilding_type = connection.secondbuilding_type
        secondbuilding_latitude = connection.secondbuilding_latitude
        secondbuilding_longitude = connection.secondbuilding_longitude
        distance = connection.distance
        connections.append({
            "mainbuilding_id": mainbuilding_id,
            "firstbuilding_id": firstbuilding_id,
            "firstbuilding_type": firstbuilding_type,
            "firstbuilding_latitude": firstbuilding_latitude,
            "firstbuilding_longitude": firstbuilding_longitude,
            "secondbuilding_id": secondbuilding_id,
            "secondbuilding_type": secondbuilding_type,
            "secondbuilding_latitude": secondbuilding_latitude,
            "secondbuilding_longitude": secondbuilding_longitude,
            "distance": distance
        })

    for pair in connections:
        coordinates[pair["firstbuilding_id"]] = [pair["firstbuilding_latitude"], pair["firstbuilding_longitude"]]
        coordinates[pair["secondbuilding_id"]] = [pair["secondbuilding_latitude"], pair["secondbuilding_longitude"]]

    for pair in connections:
        if not pair["firstbuilding_id"] in translated_connections:
            translated_connections[pair["firstbuilding_id"]] = [[pair["secondbuilding_id"], pair["distance"]]]
        else:
            translated_connections[pair["firstbuilding_id"]].append([pair["secondbuilding_id"], pair["distance"]])

    def calculate_temperatures():
        # Queue for BFS
        queue = []

        # Initialize with red buildings
        for red_building in RedBuilding.query.all():
            exit_temperature = red_building.exitTemperature
            flow_rate = red_building.flowRate
            building_id = red_building.buildingId
            temperatures[building_id] = [0, exit_temperature]
            queue.append((building_id, exit_temperature, flow_rate))

        while queue:
            current_building, current_exit_temp, current_flow_rate = queue.pop(0)
            visited.add(current_building)

            for neighbor, distance in translated_connections.get(current_building, []):
                if neighbor not in visited:
                    type_of_connection = BlueBuilding.query.filter_by(buildingId=neighbor).first().connectionType
                    DeltaT = BlueBuilding.query.filter_by(buildingId=neighbor).first().DeltaT
                    if type_of_connection == "Ground":
                        entry_temp = TforcoolingGround(groundTemperature, current_exit_temp, distance, current_flow_rate, internalDiameter, pipeThickness, insulationThickness, pipeConductivity, insulationConductivity)
                    elif type_of_connection == "Inside":
                        entry_temp = TforcoolingInside(ambientTemperature, current_exit_temp, distance, current_flow_rate, internalDiameter, pipeThickness, insulationThickness, pipeConductivity, emissivity, insulationConductivity)
                    elif type_of_connection == "Air":
                        entry_temp = TforcoolingAir(ambientTemperature, current_exit_temp, distance, current_flow_rate, internalDiameter, pipeThickness, insulationThickness, pipeConductivity, emissivity, insulationConductivity, airVelocity,irradiance)

                    outlet_temp = entry_temp + DeltaT
                    temperatures[neighbor] = [entry_temp, outlet_temp]

                    # Add the neighbor to the queue to process its neighbors
                    queue.append((neighbor, outlet_temp, current_flow_rate))

    calculate_temperatures()

    for building_id, temps in temperatures.items():
        entry_temperature = temps[0]
        exit_temperature = temps[1]
        latitude, longitude = coordinates.get(building_id, [0, 0])
        h_temp = Cold_Temperatures(
            building_id=building_id,
            building_latitude=latitude,
            building_longitude=longitude,
            inlet_temperature=entry_temperature,
            exit_temperature=exit_temperature
        )
        db.session.add(h_temp)
    
    db.session.commit()
    return temperatures, translated_connections,coordinates