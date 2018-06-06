!------ Beschreibung --------------------------------
! .nc-files werden in .txt files umgwandelt. 
! Name des .nc-files wird über bash eingelesen und steckt in var.

program netcdf_read
  use netcdf
  implicit none
  
  INTEGER :: b
!  CHARACTER(len=100) :: arg

  type :: koord
    real :: lat
    real :: lon
    real :: lat_rot
    real :: lon_rot
    real :: n = 0                                     !< 1 wenn punkt in niedersachsen liegt, sonst 0
  end type koord  

  integer :: ncid
  integer :: tas_varid

  integer :: nDims, nVars, nGlobalAtts, unlimdimid
  integer :: tas_dim, tas_att, tas_len, i, j, p, g, m, n,v 
  integer :: lat_start, lat_end, lon_start, lon_end
  real :: lat_min_n, lat_max_n, lon_max_n, lon_min_n
  real :: dummy1, dummy2 
  real, parameter :: s_to_m30 = 30*24*60*60
  real, parameter :: s_to_m31 = 31*24*60*60
  
  integer, dimension(nf90_max_var_dims) :: tas_dimids
  
  character(len = nf90_max_name) :: tasDimName
  character(len = nf90_max_name) :: att_name

  character (len = *), parameter :: LAT_NAME = "rlat"
  character (len = *), parameter :: LON_NAME = "rlon"
  character (len = *), parameter :: TIME_NAME = "time"
  integer :: lat_dimid, lon_dimid, time_dimid
  integer :: lat_varid, lon_varid, time_varid, lat_id 
  integer :: numDimLat, numDimLon, numDimtime
  integer :: NLATS, NLONS, NTIME, numLats, numLons, numTimes
  integer, dimension(nf90_max_var_dims) :: dimIDs
    
  integer, parameter :: lon_start_ind = 1
  integer, PARAMETER :: lon_end_ind = 83
  integer, parameter :: lat_start_ind = 1 
  integer, parameter :: lat_end_ind = 47
    
  ! This is the name of the data file we will read and output
!  character (len = *), parameter :: FILE_IN = "pr_EUR-11_CNRM-CERFACS-CNRM-CM5_historical_r1i1p1_CLMcom-CCLM4-8-17_v1_mon_" !60
!  character (len = 100) :: FILE_NAME = "pr_EUR-11_CNRM-CERFACS-CNRM-CM5_historical_r1i1p1_CLMcom-CCLM4-8-17_v1_mon_0.nc"
  character (len = 300) :: FILE_OUT
  character (len = 300) :: FILE_NAME
  character (len = 1) :: out_index 
  character (len = 3) :: length_out_path_str !6 weil tasmax längste ist
  character(len=:), allocatable :: out_path 
  integer :: length_out_path
  character (len = 6) :: var
  
  real, dimension(:), allocatable :: lats_rot
  real, dimension(:), allocatable :: lons_rot
  real, dimension(:), allocatable :: lats
  real, dimension(:), allocatable :: lons  
  real, dimension(:), allocatable :: time  
  real, dimension(:, :, :), allocatable :: tas_in 
  type( koord ), dimension(:,:), allocatable :: lat_lon
  type( koord ), dimension(lat_end_ind,lon_end_ind) :: lat_lon_n             !< gitter für niedersachsen mit 12,5km abstand 
    
  character(len = nf90_max_name) :: name 
  
!------ einlesen von filename und outpath -----
     call getarg(1, FILE_NAME)
     call getarg(2, out_index)
     call getarg(3, length_out_path_str)
     read(length_out_path_str,'(I3)') length_out_path 
     allocate(character(len=length_out_path) :: out_path)
     call getarg(4, out_path)
     call getarg(5, var)
    
    
!----- Open the file. 
    call check( nf90_open(trim(FILE_NAME), nf90_nowrite, ncid) )

    call check( nf90_inquire(ncid, nDims, nVars, nGlobalAtts, unlimdimid))

!----- Get the varids of the latitude and longitude coordinate variables.
    call check( nf90_inq_varid(ncid, LAT_NAME, lat_varid) )
    call check( nf90_inq_varid(ncid, LON_NAME, lon_varid) )
    call check( nf90_inq_varid(ncid, TIME_NAME, time_varid) )
    call check( nf90_inq_varid(ncid, var, tas_varid))    

!----- Get the length of the dimensions         
    call check( nf90_inq_dimid(ncid, LAT_NAME, lat_dimid))
    call check( nf90_inq_dimid(ncid, LON_NAME, lon_dimid))
    call check( nf90_inq_dimid(ncid, TIME_NAME, time_dimid))
    
    call check( nf90_inquire_dimension(ncid, lat_dimid, len = numLats))
    call check( nf90_inquire_dimension(ncid, lon_dimid, len = numLons))   
    call check( nf90_inquire_dimension(ncid, time_dimid, len = numTimes))    
    
!----- Initialize the data arrays    
    allocate(lats_rot(numLats))
    allocate(lons_rot(numLons))
!     allocate(lats_rot_gp(numLats))
!     allocate(lons_rot_gp(numLons))    
    allocate(lats(numLats))
    allocate(lons(numLons))
    allocate(time(numTimes))
    allocate(tas_in(numLons, numLats, numTimes))
    allocate(lat_lon(numLats, numLons))
    
!----- Read the latitude and longitude and tas data.
    call check( nf90_get_var(ncid, lat_varid, lats_rot) )     
    call check( nf90_get_var(ncid, lon_varid, lons_rot) )  
    call check( nf90_get_var(ncid, tas_varid, tas_in) )

!----- rotiertes Gitter anlegen aus eingelesenen daten mit geo daten drin    
    do i = 1, numLats
        do j = 1, numLons
            call coord_trafo(2, lats_rot(i), lons_rot(j), lat_lon(i,j))
        end do   
    end do

    
!------ Niedersachsen Gitter initiieren mit Auflösung 12,5km ---------------
    do i=lat_start_ind, lat_end_ind 
        lat_lon_n(i,:)%lat = (51.31250-0.125) + (i-1)*0.0625
        lat_lon_n(i,:)%n = 1
    end do
    
    do i=lon_start_ind, lon_end_ind 
        lat_lon_n(:,i)%lon = (6.68750-0.125) + (i-1)*0.0625
        lat_lon_n(:,i)%n = 1
    end do
    
    do i=lat_start_ind, lat_end_ind
        do j=lon_start_ind, lon_end_ind
              dummy1 = lat_lon_n(i,j)%lat 
              dummy2 = lat_lon_n(i,j)%lon
              call coord_trafo(1, dummy1, dummy2, lat_lon_n(i,j))
        end do
    end do 
    

!------ Niedersachsen misslons/misslats fur Auflösung 12.5km initiieren --------------
!  do i = lat_start_ind, lat_end_ind !Breitengrade
!  end do


!------ gp, die nahe an gp aus lat_lon_n aus niedersachsen sind  
  lat_min_n = minval(lat_lon_n(:,:)%lat_rot)
  lat_max_n = maxval(lat_lon_n(:,:)%lat_rot)
  lon_min_n = minval(lat_lon_n(:,:)%lon_rot)
  lon_max_n = maxval(lat_lon_n(:,:)%lon_rot)

!------ indizes der grenzen suchen 
  do i = 1, numLats
    do j = 1, numLons
        if(lat_lon(i,j)%lat_rot <= lat_max_n+0.055 .AND. lat_lon(i,j)%lat_rot >= lat_max_n-0.055) then
            lat_end = i
            !print *, lat_lon(i,j)%lat_rot, lat_lon(i,j)%lat
        else if(lat_lon(i,j)%lat_rot <= lat_min_n+0.055 .AND. lat_lon(i,j)%lat_rot >= lat_min_n-0.055) then
            lat_start = i
            !print *, lat_lon(i,j)%lat_rot
        else if(lat_lon(i,j)%lon_rot <= lon_max_n+0.055 .AND. lat_lon(i,j)%lon_rot >= lon_max_n-0.055) then
            lon_end = j
        else if(lat_lon(i,j)%lon_rot <= lon_min_n+0.055 .AND. lat_lon(i,j)%lon_rot >= lon_min_n-0.055) then
            lon_start = j
        end if    
    end do
  end do   


!----- eingelesene daten niedersachsen zuordnen  
   do i = lat_start_ind, lat_end_ind
     do j = lon_start_ind, lon_end_ind
         if(lat_lon_n(i,j)%n == 1) then
             do m = lat_start, lat_end
                 do n = lon_start, lon_end
                     if((lat_lon(m,n)%lat_rot-0.055 < lat_lon_n(i,j)%lat_rot .AND. &
                         lat_lon(m,n)%lat_rot+0.055 > lat_lon_n(i,j)%lat_rot) .AND. &            
                         (lat_lon(m,n)%lon_rot-0.055 < lat_lon_n(i,j)%lon_rot .AND. &
                         lat_lon(m,n)%lon_rot+0.055 > lat_lon_n(i,j)%lon_rot) ) then
                             lat_lon(m,n)%n = 1
                             !print *, lat_lon(m,n)%lon, lat_lon(m,n)%lat
                     end if
                 end do
             end do
         end if
     end do
   end do   



  
!----- Einlesen in .txt-File -------------------------
    write(FILE_OUT,"(A,A)") trim(out_path),".txt"
    
    open(21,file=trim(FILE_OUT),status='replace',action='write')
    
!------ rotierte daten einlesen (anderes format)    
        do g = 1, numTimes
            do i = lat_start, lat_end
                do j = lon_start, lon_end
                    if (lat_lon(i,j)%n == 1) then
                        if (mod(g,2) == 0) then
                            if ( trim(var) == 'pr' ) then
                                write(21,'(I0,F8.5,1X,F0.5,1X,F0.5)') g, lat_lon(i,j)%lat_rot, lat_lon(i,j)%lon_rot,&
                                tas_in(j,i,g)*s_to_m30
                            else if ( trim(var) == 'tas' .or. trim(var) == 'tasmax' .or. trim(var) == 'tasmin') then
                                write(21,'(I0,F8.5,1X,F0.5,1X,F0.5)') g, lat_lon(i,j)%lat_rot, lat_lon(i,j)%lon_rot,&
                                tas_in(j,i,g)
                            end if    
                        else if (mod(g,2) == 1) then
                            if ( trim(var) == 'pr' ) then
                                write(21,'(I0,F8.5,1X,F0.5,1X,F0.5)') g, lat_lon(i,j)%lat_rot, lat_lon(i,j)%lon_rot,&
                                tas_in(j,i,g)*s_to_m31
                            else if ( trim(var) == "tas" .or. trim(var) == 'tasmax' .or. trim(var) == 'tasmin') then
                                write(21,'(I0,F8.5,1X,F0.5,1X,F0.5)') g, lat_lon(i,j)%lat_rot, lat_lon(i,j)%lon_rot,&
                                tas_in(j,i,g)
                            end if    
                        end if    
                    end if
                end do
            end do
        end do
!         do g = 1, numTimes
!             do i = lat_start, lat_end
!                 do j = lon_start, lon_end
!                     if (lat_lon(i,j)%n == 1) then
!                         write(21+p,*) g, lat_lon(i,j)%lat_rot, lat_lon(i,j)%lat, &
!                         lat_lon(i,j)%lon_rot, lat_lon(i,j)%lon, tas_in(j,i,g)
!                     end if
!                 end do
!             end do
!         end do

        
!------- nicht rotierte daten einlesen

!         do g = 1, numTimes
!             do i = lat_start, lat_end
!                 do j = lon_start, lon_end
!                     if (lat_lon(i,j)%n == 1) then
!                         write(21+p,*) g, lat_lon(i,j)%lat, lat_lon(i,j)%lon, lat_lon(i,j)%lat_rot, &
!                         lat_lon(i,j)%lon_rot
!                     end if
!                 end do
!             end do
!         end do

     call check( nf90_close(ncid) )
    

!----- If we got this far, everything worked as expected. Yipee! 
    print *,"*** SUCCESS reading file!"

!----- deallocate
  deallocate(lons)
  deallocate(lats)
  deallocate(time)
  deallocate(tas_in)
  deallocate(lat_lon)
  deallocate(lats_rot)
  deallocate(lons_rot)
  deallocate(out_path)
  

contains
  subroutine check(status)
    integer, intent ( in) :: status
    
    if(status /= nf90_noerr) then 
        print *, trim(nf90_strerror(status))
        stop "Stopped"
    end if
  end subroutine check 
  
  subroutine coord_trafo(k, lat, lon, lat_lon_out)
    REAL, PARAMETER :: pi = 3.14159265359
    real, intent(in) :: lat, lon
    integer, intent(in) :: k
    real ::theta, lat_new, lon_rad, lat_rad
    real :: phi, lon_new
    real :: x, y, z, x_new, y_new, z_new
    type(koord), intent(out) :: lat_lon_out
    
    lat_rad = lat*pi/180.0
    lon_rad = lon*pi/180.0
    theta = 50.75*pi/180.0
    phi = 18.0*pi/180.0
    x = cos(lon_rad)*cos(lat_rad)
    y = sin(lon_rad)*cos(lat_rad)
    z = sin(lat_rad)
    
    if(k == 1) then !geo zu rot
        x_new = cos(theta)*cos(phi) * x + sin(phi)*cos(theta)*y + sin(theta)*z
        y_new = -sin(phi) * x + cos(phi) * y
        z_new = -cos(phi) * sin(theta) * x - sin(phi)*sin(theta)*y + cos(theta)* z
        lat_new = asin(z_new)
        lon_new = atan2(y_new, x_new)
        lat_lon_out%lat_rot = lat_new*180.0/pi
        lat_lon_out%lon_rot = lon_new*180.0/pi
        lat_lon_out%lat = lat
        lat_lon_out%lon = lon
        
    else if(k == 2) then ! rot zu geo
        theta = -theta
        phi = -phi
        x_new = cos(theta)*cos(phi) * x + sin(phi)*y + sin(theta) * cos(phi)*z
        y_new = -cos(theta) * sin(phi) * x + cos(phi)*y - sin(theta)*sin(phi) * z
        z_new = -sin(theta) * x + cos(theta) * z
        lat_new = asin(z_new)
        lon_new = atan2(y_new, x_new)
        lat_lon_out%lat = lat_new*180.0/pi
        lat_lon_out%lon = lon_new*180.0/pi
        lat_lon_out%lat_rot = lat
        lat_lon_out%lon_rot = lon

    else 
        print *, "falsches k!"
    end if    
    
  end subroutine coord_trafo  
   
  
end program

  


