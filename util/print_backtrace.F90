subroutine print_backtrace

  use iso_c_binding
  implicit none
  integer, parameter :: MAX_FRAMES = 100
  ! tableau d'adresses
  type(c_ptr), target :: frames(MAX_FRAMES)
  integer(c_int) :: nframes
  type(c_ptr) :: symbols_ptr
  type(c_ptr), pointer :: symbols(:)
  character(len=6) :: random_name
  integer :: random_int, i, digit
  integer, parameter :: min_val = 100000, max_val = 999999
  real :: random_real
 
  
 

  interface
    function backtrace(buffer, size) bind(C,name="backtrace")
      use iso_c_binding
      integer(c_int) :: backtrace
      type(c_ptr), value :: buffer
      integer(c_int), value :: size
    end function
    function backtrace_symbols(buffer,size) bind(C,name="backtrace_symbols")
      use iso_c_binding
      type(c_ptr) :: backtrace_symbols
      type(c_ptr), value :: buffer
      integer(c_int), value :: size
    end function
    subroutine free(ptr) bind(C,name="free")
      use iso_c_binding
      type(c_ptr), value :: ptr
    end subroutine
  end interface
  

    

  




       ! Générer un entier aléatoire entre 100000 et 999999
    call random_number(random_real)
    random_int = min_val + floor(random_real * (max_val - min_val + 1))

    ! Convertir l'entier en chaîne de caractères
    write(random_name, '(I6)') random_int

  ! récupération de la pile
  
  nframes = backtrace(c_loc(frames), MAX_FRAMES)
  print *, "Number of frames :", nframes

  ! char **
  symbols_ptr = backtrace_symbols(c_loc(frames), nframes)
  if (.not. c_associated(symbols_ptr)) then
     print *, "backtrace_symbols failed"
     stop
  endif
  call c_f_pointer(symbols_ptr, symbols, [nframes])
  do i = 1, nframes
     call print_c_string(symbols(i))
  enddo
  call free(symbols_ptr)
  call system("awk '!seen[$0]++' "//random_name)
  call FLUSH(6)
  call system("rm "//random_name)
contains

  subroutine print_c_string(ptr)
    use iso_c_binding
    type(c_ptr), value :: ptr
    character(kind=c_char), pointer :: str(:)
    integer :: n,start_pos,end_pos
    character(len=:), allocatable :: line
    character(len=256) :: executable_name

    call getarg(0,executable_name)

    ! taille arbitraire suffisante pour une ligne backtrace
    call c_f_pointer(ptr, str, [4096])
    n = 0
    do while (str(n+1) /= c_null_char)
       n = n + 1
    enddo
    allocate(character(len=n) :: line)
    do concurrent (i=1:n)
       line(i:i) = str(i)
    enddo
    
 !   write(*,'(A)') trim(line)
    start_pos=INDEX(line,'[')
    end_pos=INDEX(line,']')
    !write(*,'(A)') trim(line(start_pos+1:end_pos-1))
    !write(6,*) "addr2line -e "//trim(executable_name) //" "//trim(line(start_pos+1:end_pos-1)) //" >>" // random_name
    call system("addr2line -e "//trim(executable_name) //" "//trim(line(start_pos+1:end_pos-1)) //" >>" // random_name //" 2>&1")
    deallocate(line)
  end subroutine print_c_string

end subroutine print_backtrace

