module TestTrash exposing (..)

import Trash.Scalar

import Model exposing (..)
import Update exposing (..)
import View
import Main

import Expect exposing (Expectation)
import Fuzz exposing (Fuzzer, float, intRange, list, string)
import Test exposing (..)

testPage : TrashPage
testPage =
    { emptyPage
    | volume = Just 1
    , timestamp = 1533006358000
    , changed = False
    }

testChangeAmount : Test
testChangeAmount = describe "Test ChangeAmount"
    [ fuzz (intRange 0 10) "ChangeAmount changes amount of trash" <| \i ->
        let txt = toString i
            x = toFloat i
            newPage = { testPage | volume = Just x, changed = True }
        in Expect.equal
            ( update (ChangeAmount txt) testPage )
            ( newPage, Cmd.none )

    , fuzz (intRange -10 -1) "ChangeAmount rejects numbers < 0" <| \i ->
        let txt = toString i
            newPage =
                { testPage
                | error = Just "Amount must be 0 or more"
                , volume = Nothing
                , changed = True
                }
        in Expect.equal
            ( update (ChangeAmount txt) testPage )
            ( newPage, Cmd.none)

    , test "ChangeAmount rejects text strings" <| \_ ->
        let newPage =
            { testPage
            | error = Just "Amount must be a number"
            , volume = Nothing
            , changed = True
            }
        in Expect.equal
            ( update (ChangeAmount "oops") testPage )
            ( newPage, Cmd.none )

    , test "ChangeAmount with empty string is Nothing" <| \_ ->
        let newPage = { testPage | volume = Nothing, changed = True }
        in Expect.equal
            ( update (ChangeAmount "") testPage)
            ( newPage, Cmd.none )
    ]

testRelativeDate : Test
testRelativeDate = describe "relativeDate"
    [ test "Today is relatively accurate" <| \_ ->
        Expect.equal
            ( relativeDate testPage.timestamp Today )
            ( Trash.Scalar.Date "2018-07-30" )
    , test "Yesterday is relatively accurate" <| \_ ->
        Expect.equal
            ( relativeDate testPage.timestamp Yesterday )
            ( Trash.Scalar.Date "2018-07-29" )
    , test "TwoDaysAgo is relatively accurate" <| \_ ->
        Expect.equal
            ( relativeDate testPage.timestamp TwoDaysAgo )
            ( Trash.Scalar.Date "2018-07-28" )
    ]
