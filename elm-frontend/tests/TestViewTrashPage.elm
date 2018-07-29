module TestViewTrashPage exposing (..)

import Expect exposing (Expectation)
import Fuzz exposing (Fuzzer, int, intRange, list, string)
import Test exposing (..)

import Date

import Models exposing (..)
import ViewTrashPage  exposing (..)


suite : Test
suite = describe "Test ViewTrashPage"
    [ fuzz (intRange 2 100) "sayAmount gives an amount in gallons" <| \i ->
        let x = toFloat i
            str = toString i
            words = sayAmount (Gallons x)
        in Expect.equal words (str ++ " gallons of trash")

    , test "sayAmount with 1 gallon is singular" <| \_ ->
        Expect.equal (sayAmount (Gallons 1)) "1 gallon of trash"

    , test "sayAmount says 0 gallons is nothing" <| \_ ->
        Expect.equal (sayAmount (Gallons 0)) "nothing"

    , fuzz (intRange 2 100) "sayAmount gives an amount in litres" <| \i ->
        let x = toFloat i
            str = toString i
            words = sayAmount (Litres x)
        in Expect.equal words (str ++ " litres of trash")

    , test "sayAmount with 1 litre is singular" <| \_ ->
        Expect.equal (sayAmount (Litres 1)) "1 litre of trash"

    , test "sayAmount says 0 litres is nothing" <| \_ ->
        Expect.equal (sayAmount (Litres 0)) "nothing"
    ]
