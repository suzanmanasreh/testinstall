program test
    use f95_lapack, only: la_gesv

    real(kind(1.D0)) :: A(3, 3), b(3)

    call random_number(A)
    b(:) = 3*A(:,1) + 2*A(:, 2) - A(:,3)

    ! Solve Ax = b, overwrite b with solution
    call la_gesv(A, b)

    print *, b

end program test